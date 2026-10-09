# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2026 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import json
import requests
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.XMLObject import XMLObject

# These models accept function tools on /v1/responses only.
RESPONSES_ONLY_TOOL_MODEL_PREFIX_TUPLE = ('gpt-5', 'o1', 'o3', 'o4')

# The exact server answer that says the request must go to /v1/responses.
RESPONSES_REDIRECT_TEXT = 'use /v1/responses'

# Microsoft Foundry and Azure OpenAI: public cloud, Government and China.
# NOTE: `.cloudapp.azure.com` is one Azure virtual machine, not Azure OpenAI.
AZURE_OPENAI_HOST_SUFFIX_TUPLE = (
  '.services.ai.azure.com', '.openai.azure.com',
  '.cognitiveservices.azure.com',
  '.services.ai.azure.us', '.openai.azure.us',
  '.cognitiveservices.azure.us',
  '.services.ai.azure.cn', '.openai.azure.cn',
  '.cognitiveservices.azure.cn',
)

# Seconds. Used when the connector holds no Timeout property.
DEFAULT_TIMEOUT = 180

# Seconds. A background call never waits for the generation.
BACKGROUND_TIMEOUT = 30

TERMINAL_STATUS_TUPLE = ('completed', 'failed', 'incomplete', 'cancelled')

# WARNING: background mode needs "store": true, so the provider keeps the
# request and the answer. Do not send secret data to an untrusted provider.


class OpenaiConnector(XMLObject):
  meta_type = "ERP5 Openai Connector"
  portal_type = "Openai Connector"

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _getBaseUrl(self):
    url = self.getUrlString() or "https://api.openai.com/v1"
    return url.rstrip("/")

  def _getTimeout(self, default=DEFAULT_TIMEOUT):
    # The SocketClient property sheet holds Timeout. It can be absent.
    getTimeout = getattr(self, "getTimeout", None)
    if getTimeout is None:
      return default
    return getTimeout(default)

  def _buildMessages(self, prompt, message):
    if message:
      return [{"role": "user", "content": message}]
    return [{"role": "user", "content": prompt}]

  security.declareProtected(Permissions.AccessContentsInformation, 'getModelList')
  def getModelList(self):
    api_key = self.getPassword()
    base_url = self._getBaseUrl()
    headers = {"Authorization": "Bearer %s" % api_key}
    resp = requests.get(base_url + "/models", headers=headers, timeout=self._getTimeout())
    resp.raise_for_status()
    data = resp.json()
    return [m.get("id") for m in data.get("data", [])]

  # /v1/responses uses other shapes. The methods below translate them, so the
  # caller sees the Chat Completions shape only.

  def _buildResponsesInput(self, chat_message_list):
    input_list = []
    for message in chat_message_list:
      role = message.get("role")
      content = message.get("content")
      if role == "tool":
        input_list.append({
          "type": "function_call_output",
          "call_id": message.get("tool_call_id"),
          "output": content or "",
        })
        continue
      if role == "assistant" and message.get("tool_calls"):
        if content:
          input_list.append({"role": "assistant", "content": content})
        for tool_call in message["tool_calls"]:
          function = tool_call.get("function") or {}
          input_list.append({
            "type": "function_call",
            "call_id": tool_call.get("id"),
            "name": function.get("name"),
            "arguments": function.get("arguments") or "{}",
          })
        continue
      if content:
        input_list.append({"role": role or "user",
                           "content": self._buildResponsesContent(content)})
    return input_list

  def _buildResponsesContent(self, content):
    # WARNING: a plain text content must reach the provider unchanged.
    # Only the parts of a list change: input_text and a flat input_file.
    if not isinstance(content, list):
      return content
    part_list = []
    for part in content:
      if not isinstance(part, dict):
        part_list.append(part)
        continue
      part_type = part.get("type")
      if part_type == "text":
        part_list.append({"type": "input_text", "text": part.get("text")})
      elif part_type == "file":
        file_map = part.get("file") or {}
        part_list.append({"type": "input_file",
                          "file_id": file_map.get("file_id")})
      else:
        part_list.append(part)
    return part_list

  def _buildResponsesToolList(self, tool_list):
    # The Responses tool shape is flat. It has no "function" key.
    responses_tool_list = []
    for tool in tool_list or []:
      function = tool.get("function")
      if function is None:
        responses_tool_list.append(tool)
        continue
      responses_tool_list.append({
        "type": "function",
        "name": function.get("name"),
        "description": function.get("description", ""),
        "parameters": function.get("parameters") or {"type": "object", "properties": {}},
      })
    return responses_tool_list

  def _buildResponsesToolChoice(self, tool_choice):
    # /v1/responses names a function as {"type": "function", "name": "x"}.
    if not isinstance(tool_choice, dict):
      return tool_choice
    function = tool_choice.get("function")
    if isinstance(function, dict) and function.get("name"):
      return {"type": "function", "name": function["name"]}
    return tool_choice

  def _buildResponsesTextFormat(self, response_format):
    # /v1/responses holds the keys of the json_schema map at the top level.
    if not isinstance(response_format, dict):
      return response_format
    if response_format.get("type") != "json_schema":
      return response_format
    schema_map = response_format.get("json_schema")
    if not isinstance(schema_map, dict):
      return response_format
    text_format = {"type": "json_schema"}
    for key in ("name", "description", "schema", "strict"):
      if key in schema_map:
        text_format[key] = schema_map[key]
    return text_format

  def _parseResponsesAnswer(self, data, model, file_id=None):
    # The Chat Completions keys, plus id, status, is_done and error.
    content_part_list = []
    tool_call_list = []
    for item in data.get("output") or []:
      item_type = item.get("type")
      if item_type == "message":
        for part in item.get("content") or []:
          if part.get("type") == "output_text" and part.get("text"):
            content_part_list.append(part["text"])
      elif item_type == "function_call":
        tool_call_list.append({
          "id": item.get("call_id") or item.get("id"),
          "type": "function",
          "function": {
            "name": item.get("name"),
            "arguments": item.get("arguments") or "{}",
          },
        })
    usage = data.get("usage") or {}
    # A blocking call answers no status, and its answer is complete.
    status = data.get("status") or "completed"
    return {
      "id": data.get("id"),
      "status": status,
      "is_done": status in TERMINAL_STATUS_TUPLE,
      "content": "\n".join(content_part_list),
      "tool_calls": tool_call_list,
      "model": data.get("model", model) or model,
      "usage": {
        "prompt_tokens": int(usage.get("input_tokens", 0) or 0),
        "completion_tokens": int(usage.get("output_tokens", 0) or 0),
        "total_tokens": int(usage.get("total_tokens", 0) or 0),
        "cached_tokens": self._cachedTokenCount(usage),
      },
      "error": self._parseResponsesError(data),
      "file_id": file_id,
    }

  def _parseResponsesError(self, data):
    # An incomplete response holds "incomplete_details", not "error".
    error = data.get("error")
    if isinstance(error, dict) and (error.get("code") or error.get("message")):
      return {
        "code": "%s" % (error.get("code") or "", ),
        "message": "%s" % (error.get("message") or "", ),
      }
    detail = data.get("incomplete_details")
    if isinstance(detail, dict) and detail.get("reason"):
      return {"code": "incomplete", "message": "%s" % (detail["reason"], )}
    return None


  def _cachedTokenCount(self, usage):
    # Chat Completions and Responses name the detail map differently.
    for name in ("prompt_tokens_details", "input_tokens_details"):
      detail = usage.get(name)
      if isinstance(detail, dict):
        try:
          return int(detail.get("cached_tokens", 0) or 0)
        except Exception:
          return 0
    return 0

  def _needResponsesApi(self, model, tools):
    # Answer True when the model refuses function tools on Chat Completions.
    if not tools:
      return False
    model_name = (model or "").lower()
    for prefix in RESPONSES_ONLY_TOOL_MODEL_PREFIX_TUPLE:
      if model_name.startswith(prefix):
        return True
    return False

  def _getHostName(self, url):
    host = url.split("://")[-1].split("/")[0].split("@")[-1]
    return host.split(":")[0]

  def _isAzureProvider(self):
    host_name = self._getHostName(self._getBaseUrl().lower())
    return host_name.endswith(AZURE_OPENAI_HOST_SUFFIX_TUPLE)

  def _getUploadPurpose(self):
    # Microsoft Foundry refuses the purpose "user_data" for one input file of
    # the Responses API. Microsoft Foundry needs the purpose "assistants".
    if self._isAzureProvider():
      return "assistants"
    return "user_data"

  def _getAuthHeaderDict(self, content_type=None):
    header_dict = {"Authorization": "Bearer %s" % self.getPassword()}
    if content_type is not None:
      header_dict["Content-Type"] = content_type
    return header_dict

  def _getRequestKw(self, cert=None, verify=None):
    request_kw = {}
    if cert is not None:
      request_kw["cert"] = cert
    if verify is not None:
      request_kw["verify"] = verify
    return request_kw

  def _buildResponsesPayload(self, chat_message_list, model, tools,
                             tool_choice, response_format, reasoning_effort,
                             prompt_cache_key=None, background=False):
    payload = {
      "model": model,
      "input": self._buildResponsesInput(chat_message_list),
    }
    if background:
      # The provider reads a background answer from its own storage.
      payload["background"] = True
      payload["store"] = True
    if prompt_cache_key:
      payload["prompt_cache_key"] = prompt_cache_key
    if tools:
      payload["tools"] = self._buildResponsesToolList(tools)
    if tool_choice is not None:
      payload["tool_choice"] = self._buildResponsesToolChoice(tool_choice)
    if reasoning_effort:
      payload["reasoning"] = {"effort": reasoning_effort}
    if response_format is not None:
      # The Responses endpoint reads the format under "text".
      payload["text"] = {
        "format": self._buildResponsesTextFormat(response_format)}
    return payload

  def _postResponses(self, payload, headers, timeout, request_kw,
                     path_suffix=""):
    # sort_keys: the same payload gives the same bytes, so a cache that
    # hashes the body answers a repeated prefix.
    url = self._getBaseUrl() + "/responses" + path_suffix
    data = None
    if payload is not None:
      data = json.dumps(payload, sort_keys=True)
    resp = requests.post(url, headers=headers, data=data, timeout=timeout,
                         **request_kw)
    if resp.status_code >= 400:
      raise ValueError("LLM %s error on /responses: %s"
                       % (resp.status_code, resp.text[:1000]))
    return resp.json()

  def _deleteFile(self, file_id, headers, request_kw):
    # Never raise: a file that stays at the provider costs storage only.
    try:
      requests.delete(self._getBaseUrl() + "/files/" + file_id,
                      headers=headers, timeout=self._getTimeout(),
                      **request_kw)
    except Exception:
      pass

  def _uploadFile(self, attachment_data, attachment_filename,
                  attachment_media_type, base_url, headers, request_kw):
    # Raise ValueError when the provider refuses the upload.
    # The upload uses the long timeout in both modes: a large file needs it.
    file_name = attachment_filename or "attachment.pdf"
    upload_resp = requests.post(
      base_url + "/files", headers=headers,
      files={"file": (file_name, attachment_data, attachment_media_type)},
      data={"purpose": self._getUploadPurpose()}, timeout=self._getTimeout(),
      **request_kw)
    if upload_resp.status_code >= 400:
      raise ValueError("LLM %s error: %s"
                       % (upload_resp.status_code, upload_resp.text[:1000]))
    return upload_resp.json()["id"]

  def _addFilePartToMessageList(self, chat_message_list, file_id):
    # The file goes into the last `user` message, the request of this round.
    # A file part in a `system` or a `tool` message breaks the shape.
    file_part = {"type": "file", "file": {"file_id": file_id}}
    new_message_list = list(chat_message_list or [])
    last_user_index = None
    for index in range(len(new_message_list)):
      if (new_message_list[index] or {}).get("role") == "user":
        last_user_index = index
    if last_user_index is None:
      new_message_list.append({"role": "user", "content": [file_part]})
      return new_message_list
    message = dict(new_message_list[last_user_index])
    content = message.get("content")
    if isinstance(content, list):
      part_list = list(content)
    elif content:
      part_list = [{"type": "text", "text": content}]
    else:
      part_list = []
    part_list.append(file_part)
    message["content"] = part_list
    new_message_list[last_user_index] = message
    return new_message_list

  def _callResponsesApi(self, chat_message_list, model, tools, tool_choice,
                        response_format, reasoning_effort, headers, timeout,
                        request_kw, prompt_cache_key=None, background=False,
                        file_id=None):
    payload = self._buildResponsesPayload(
      chat_message_list, model, tools, tool_choice, response_format,
      reasoning_effort, prompt_cache_key=prompt_cache_key,
      background=background)
    data = self._postResponses(payload, headers, timeout, request_kw)
    return self._parseResponsesAnswer(data, model, file_id=file_id)

  security.declareProtected(Permissions.AccessContentsInformation, 'createResponse')
  def createResponse(self, prompt=None, attachment_data=None, attachment_filename=None,
                  attachment_media_type="application/pdf", model="gpt-4o", message=None,
                  response_format=None, messages=None, tools=None, tool_choice=None,
                  cert=None, verify=None, timeout=None,
                  reasoning_effort=None, api_style=None,
                  prompt_cache_key=None, background=True, file_id=None):
    # WARNING: background mode is the default. Pass background=False to wait.
    # The caller owns a `file_id` that it passes, and calls `removeFile`.
    # Do not pass that `file_id` to `retrieveResponse`, which deletes the file.
    # A failed upload answers the status "failed" and does not raise.
    # Give one `prompt_cache_key` per prompt family, never one key per mail.
    if background and api_style == "chat":
      raise ValueError(
        "Chat Completions holds no background mode. "
        "Call with api_style='responses', or call with background=False.")
    if timeout is None:
      if background:
        timeout = BACKGROUND_TIMEOUT
      else:
        timeout = self._getTimeout()
    base_url = self._getBaseUrl()
    auth_headers = self._getAuthHeaderDict()
    request_kw = self._getRequestKw(cert=cert, verify=verify)

    is_file_kept = file_id is not None
    uploaded_file_id = None
    try:
      if messages is not None:
        chat_messages = messages
        if file_id is None and attachment_data is not None:
          try:
            file_id = self._uploadFile(
              attachment_data, attachment_filename, attachment_media_type,
              base_url, auth_headers, request_kw)
            uploaded_file_id = file_id
          except Exception as error:
            return {
              "id": None,
              "status": "failed",
              "is_done": True,
              "content": "",
              "tool_calls": [],
              "model": model,
              "usage": {},
              "error": {"code": "file_upload_failed",
                        "message": "%s" % (error, )},
              "file_id": None,
            }
        if file_id is not None:
          is_file_kept = True
          chat_messages = self._addFilePartToMessageList(
            chat_messages, file_id)
      elif attachment_data is not None:
        file_id = self._uploadFile(
          attachment_data, attachment_filename, attachment_media_type,
          base_url, auth_headers, request_kw)
        chat_messages = [{"role": "user",
          "content": [{"type": "text", "text": prompt},
                      {"type": "file", "file": {"file_id": file_id}}]}]
      else:
        chat_messages = self._buildMessages(prompt, message)

      chat_headers = self._getAuthHeaderDict(content_type="application/json")

      if api_style is None:
        if background or self._needResponsesApi(model, tools):
          api_style = "responses"
        elif file_id is not None and self._isAzureProvider():
          # Microsoft documents one file input on /v1/responses only.
          api_style = "responses"
        else:
          api_style = "chat"

      if api_style == "responses":
        response = self._callResponsesApi(
          chat_messages, model, tools, tool_choice, response_format,
          reasoning_effort, chat_headers, timeout, request_kw,
          prompt_cache_key=prompt_cache_key, background=background,
          file_id=file_id)
        # A background answer reads the file later. Keep the file.
        if file_id is not None and not response["is_done"]:
          is_file_kept = True
        return response

      payload = {"model": model, "messages": chat_messages}
      if prompt_cache_key:
        payload["prompt_cache_key"] = prompt_cache_key
      if response_format is not None:
        payload["response_format"] = response_format
      if tools is not None:
        payload["tools"] = tools
      if tool_choice is not None:
        payload["tool_choice"] = tool_choice
      if reasoning_effort is not None:
        payload["reasoning_effort"] = reasoning_effort
      chat_resp = requests.post(
        base_url + "/chat/completions", headers=chat_headers,
        data=json.dumps(payload, sort_keys=True),
        timeout=timeout, **request_kw)
      if chat_resp.status_code >= 400:
        # The server can ask for /v1/responses. Send the request there.
        if chat_resp.status_code == 400 and RESPONSES_REDIRECT_TEXT in chat_resp.text:
          return self._callResponsesApi(
            chat_messages, model, tools, tool_choice, response_format,
            reasoning_effort, chat_headers, timeout, request_kw,
            prompt_cache_key=prompt_cache_key, file_id=file_id)
        raise ValueError("LLM %s error: %s" % (chat_resp.status_code, chat_resp.text[:1000]))
      data = chat_resp.json()
      usage = data.get("usage") or {}
      choice_message = data["choices"][0]["message"]
      return {
        "id": data.get("id"),
        "status": "completed",
        "is_done": True,
        "content": choice_message.get("content", "") or "",
        "tool_calls": choice_message.get("tool_calls") or [],
        "model": data.get("model", model) or model,
        "usage": {
          "prompt_tokens": int(usage.get("prompt_tokens", 0) or 0),
          "completion_tokens": int(usage.get("completion_tokens", 0) or 0),
          "total_tokens": int(usage.get("total_tokens", 0) or 0),
          "cached_tokens": self._cachedTokenCount(usage),
        },
        "error": None,
        "file_id": file_id,
      }
    except:
      # Never delete a file that the caller gave.
      if uploaded_file_id is not None:
        is_file_kept = False
      raise
    finally:
      if file_id is not None and not is_file_kept:
        self._deleteFile(file_id, auth_headers, request_kw)

  def _checkResponseId(self, response_id):
    # The identifier goes into the URL. A `/`, `?` or `#` would send the API
    # key to another path.
    if not response_id:
      raise ValueError("The response identifier is empty.")
    for character in ("/", "?", "#"):
      if character in response_id:
        raise ValueError(
          "The response identifier holds the character %r." % (character, ))

  security.declareProtected(Permissions.AccessContentsInformation, 'retrieveResponse')
  def retrieveResponse(self, response_id, file_id=None, cert=None,
                       verify=None, timeout=None):
    # WARNING: a transport error and the HTTP status 404 raise. A raise is not
    # an answer. Do not end the run on it.
    self._checkResponseId(response_id)
    if timeout is None:
      timeout = BACKGROUND_TIMEOUT
    auth_headers = self._getAuthHeaderDict()
    request_kw = self._getRequestKw(cert=cert, verify=verify)
    resp = requests.get(
      self._getBaseUrl() + "/responses/" + response_id,
      headers=auth_headers, timeout=timeout, **request_kw)
    if resp.status_code >= 400:
      # WARNING: a caller reads `LLM 404 error` in this text. Do not change
      # the start of this text.
      raise ValueError("LLM %s error on /responses/%s: %s"
                       % (resp.status_code, response_id, resp.text[:1000]))
    response = self._parseResponsesAnswer(resp.json(), None, file_id=file_id)
    if file_id is not None and response["is_done"]:
      self._deleteFile(file_id, auth_headers, request_kw)
    return response

  security.declareProtected(Permissions.AccessContentsInformation, 'cancelResponse')
  def cancelResponse(self, response_id, file_id=None, cert=None, verify=None,
                     timeout=None):
    # The provider bills the tokens before the stop, so the answer holds usage.
    # Only a stored response accepts the cancel. Others answer HTTP 400.
    self._checkResponseId(response_id)
    if timeout is None:
      timeout = BACKGROUND_TIMEOUT
    auth_headers = self._getAuthHeaderDict()
    request_kw = self._getRequestKw(cert=cert, verify=verify)
    data = self._postResponses(
      None, self._getAuthHeaderDict(content_type="application/json"),
      timeout, request_kw, path_suffix="/" + response_id + "/cancel")
    response = self._parseResponsesAnswer(data, None, file_id=file_id)
    if file_id is not None and response["is_done"]:
      self._deleteFile(file_id, auth_headers, request_kw)
    return response

  # WARNING: no method of this class holds a docstring. Zope publishes no
  # method without one. `_deleteFile` hides errors, so read the status here.
  security.declareProtected(Permissions.AccessContentsInformation, 'removeFile')
  def removeFile(self, file_id, cert=None, verify=None):
    if not file_id:
      return False
    try:
      resp = requests.delete(
        self._getBaseUrl() + "/files/" + file_id,
        headers=self._getAuthHeaderDict(), timeout=self._getTimeout(),
        **self._getRequestKw(cert=cert, verify=verify))
    except Exception:
      return False
    return resp.status_code < 400
