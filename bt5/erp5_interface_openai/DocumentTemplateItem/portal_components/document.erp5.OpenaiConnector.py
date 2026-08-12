# -*- coding: utf-8 -*-
import json
import requests
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.XMLObject import XMLObject
from zope.interface import implementer
from ZPublisher.Iterators import IUnboundStreamIterator


def _iterChatCompletionChunks(base_url, chat_headers, payload, timeout, request_kw):
  # Pure function: touches only requests/local values, no ZODB - safe to
  # iterate after the caller's request has finished and its ZODB connection
  # has closed (see OpenaiStreamIterator/getResponseStreamIterator).
  content_list = []
  tool_call_map = {}
  usage = {}
  response_model = payload.get("model")

  chat_resp = requests.post(
    base_url + "/chat/completions", headers=chat_headers,
    json=payload, timeout=timeout, stream=True, **request_kw)
  if chat_resp.status_code >= 400:
    raise ValueError("LLM %s error: %s" % (chat_resp.status_code, chat_resp.text[:1000]))

  for raw_line in chat_resp.iter_lines():
    if not raw_line:
      continue
    line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
    if not line.startswith("data:"):
      continue
    data_str = line[len("data:"):].strip()
    if data_str == "[DONE]":
      break
    chunk = json.loads(data_str)
    response_model = chunk.get("model", response_model) or response_model
    if chunk.get("usage"):
      chunk_usage = chunk["usage"]
      usage = {
        "prompt_tokens": int(chunk_usage.get("prompt_tokens", 0) or 0),
        "completion_tokens": int(chunk_usage.get("completion_tokens", 0) or 0),
        "total_tokens": int(chunk_usage.get("total_tokens", 0) or 0),
      }
    choices = chunk.get("choices") or []
    if not choices:
      continue
    delta = choices[0].get("delta") or {}
    delta_content = delta.get("content")
    if delta_content:
      content_list.append(delta_content)
      yield {"type": "delta", "content": delta_content}
    for tool_call_delta in delta.get("tool_calls") or []:
      index = tool_call_delta.get("index", 0)
      entry = tool_call_map.setdefault(index, {
        "id": "", "type": "function", "function": {"name": "", "arguments": ""}})
      if tool_call_delta.get("id"):
        entry["id"] = tool_call_delta["id"]
      if tool_call_delta.get("type"):
        entry["type"] = tool_call_delta["type"]
      function_delta = tool_call_delta.get("function") or {}
      if function_delta.get("name"):
        entry["function"]["name"] += function_delta["name"]
      if function_delta.get("arguments"):
        entry["function"]["arguments"] += function_delta["arguments"]

  tool_calls = [tool_call_map[index] for index in sorted(tool_call_map)]
  yield {
    "type": "final",
    "content": "".join(content_list),
    "tool_calls": tool_calls,
    "model": response_model,
    "usage": usage or {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
  }


@implementer(IUnboundStreamIterator)
class OpenaiStreamIterator(object):
  # Wraps a chunk generator so ZPublisher recognizes it (via the interface
  # declaration above) and hands it straight to the WSGI server as the
  # response body, instead of buffering the whole thing in memory first.
  def __init__(self, chunk_generator):
    self._chunk_generator = chunk_generator

  def __iter__(self):
    return self

  def __next__(self):
    return (json.dumps(next(self._chunk_generator)) + "\n").encode("utf-8")

  next = __next__


class OpenaiConnector(XMLObject):
  meta_type = "ERP5 Openai Connector"
  portal_type = "Openai Connector"

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _getBaseUrl(self):
    url = self.getUrlString() or "https://api.openai.com/v1"
    return url.rstrip("/")

  def _buildMessages(self, prompt, attachment_data, attachment_filename,
                     attachment_media_type, message):
    if message:
      return [{"role": "user", "content": message}]
    if attachment_data is not None:
      return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user",   "content": prompt},
        {"role": "user",
         "content": [{"type": "file",
                      "file": {"filename": attachment_filename or "document.pdf",
                               "file_data": attachment_data}}]},
      ]
    return [{"role": "user", "content": prompt}]

  security.declarePublic("getModelList")
  def getModelList(self):
    # Return the list of model ids the OpenAI-compatible server exposes.
    api_key = self.getPassword()
    base_url = self._getBaseUrl()
    headers = {"Authorization": "Bearer %s" % api_key}
    resp = requests.get(base_url + "/models", headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return [m.get("id") for m in data.get("data", [])]

  security.declarePublic("getResponseWithUsage")
  def getResponseWithUsage(self, prompt=None, attachment_data=None, attachment_filename=None,
                  attachment_media_type="application/pdf", model="gpt-4o", message=None,
                  response_format=None, messages=None, tools=None, tool_choice=None,
                  cert=None, verify=None, timeout=180):
    # Call an OpenAI-compatible Chat Completions endpoint; return
    # {content, tool_calls, model, usage}. When messages (a list) is given it is
    # used verbatim. tools/tool_choice/response_format are forwarded as-is.
    api_key = self.getPassword()
    base_url = self._getBaseUrl()
    auth_headers = {"Authorization": "Bearer %s" % api_key}
    request_kw = {}
    if cert is not None:
      request_kw["cert"] = cert
    if verify is not None:
      request_kw["verify"] = verify

    file_id = None
    try:
      if messages is not None:
        chat_messages = messages
      elif attachment_data is not None:
        fname = attachment_filename or "attachment.pdf"
        upload_resp = requests.post(
          base_url + "/files", headers=auth_headers,
          files={"file": (fname, attachment_data, attachment_media_type)},
          data={"purpose": "user_data"}, timeout=timeout, **request_kw)
        upload_resp.raise_for_status()
        file_id = upload_resp.json()["id"]
        chat_messages = [{"role": "user",
          "content": [{"type": "text", "text": prompt},
                      {"type": "file", "file": {"file_id": file_id}}]}]
      else:
        chat_messages = self._buildMessages(prompt, None, None, None, message)

      chat_headers = dict(auth_headers)
      chat_headers["Content-Type"] = "application/json"
      payload = {"model": model, "messages": chat_messages}
      if response_format is not None:
        payload["response_format"] = response_format
      if tools is not None:
        payload["tools"] = tools
      if tool_choice is not None:
        payload["tool_choice"] = tool_choice
      chat_resp = requests.post(
        base_url + "/chat/completions", headers=chat_headers,
        json=payload, timeout=timeout, **request_kw)
      if chat_resp.status_code >= 400:
        raise ValueError("LLM %s error: %s" % (chat_resp.status_code, chat_resp.text[:1000]))
      data = chat_resp.json()
      usage = data.get("usage") or {}
      choice_message = data["choices"][0]["message"]
      return {
        "content": choice_message.get("content", "") or "",
        "tool_calls": choice_message.get("tool_calls") or [],
        "model": data.get("model", model) or model,
        "usage": {
          "prompt_tokens": int(usage.get("prompt_tokens", 0) or 0),
          "completion_tokens": int(usage.get("completion_tokens", 0) or 0),
          "total_tokens": int(usage.get("total_tokens", 0) or 0),
        },
      }
    finally:
      if file_id is not None:
        try:
          requests.delete(base_url + "/files/" + file_id, headers=auth_headers, timeout=30, **request_kw)
        except Exception:
          pass

  security.declarePublic("getResponseWithUsageStream")
  def getResponseWithUsageStream(self, prompt=None, model="gpt-4o", message=None,
                  messages=None, tools=None, tool_choice=None,
                  cert=None, verify=None, timeout=180):
    # Same call as getResponseWithUsage but against the SSE streaming endpoint.
    # Everything that touches ZODB (self.getPassword(), self._getBaseUrl())
    # runs eagerly here, before the returned generator is ever iterated -
    # getResponseStreamIterator's caller relies on that to stay ZODB-free.
    # Yields {"type": "delta", "content": <piece>} as each chunk arrives, then
    # exactly one {"type": "final", "content", "tool_calls", "model", "usage"}
    # with the full accumulated answer once the stream ends.
    api_key = self.getPassword()
    base_url = self._getBaseUrl()
    request_kw = {}
    if cert is not None:
      request_kw["cert"] = cert
    if verify is not None:
      request_kw["verify"] = verify

    if messages is not None:
      chat_messages = messages
    else:
      chat_messages = self._buildMessages(prompt, None, None, None, message)

    chat_headers = {
      "Authorization": "Bearer %s" % api_key,
      "Content-Type": "application/json",
    }
    payload = {
      "model": model,
      "messages": chat_messages,
      "stream": True,
      "stream_options": {"include_usage": True},
    }
    if tools is not None:
      payload["tools"] = tools
    if tool_choice is not None:
      payload["tool_choice"] = tool_choice

    return _iterChatCompletionChunks(base_url, chat_headers, payload, timeout, request_kw)

  security.declarePublic("getResponseStreamIterator")
  def getResponseStreamIterator(self, prompt=None, model="gpt-4o", message=None,
                  messages=None, tools=None, tool_choice=None,
                  cert=None, verify=None, timeout=180):
    # Returns an IUnboundStreamIterator: hand this straight to
    # RESPONSE.setBody() so ZPublisher streams it to the client as OpenAI
    # generates it, instead of buffering the whole answer first.
    return OpenaiStreamIterator(self.getResponseWithUsageStream(
      prompt=prompt, model=model, message=message, messages=messages,
      tools=tools, tool_choice=tool_choice, cert=cert, verify=verify, timeout=timeout))

  security.declarePublic("getResponse")
  def getResponse(self, prompt, attachment_data=None, attachment_filename=None,
                  attachment_media_type="application/pdf", model="gpt-4o"):
    res = self.getResponseWithUsage(prompt=prompt, attachment_data=attachment_data,
            attachment_filename=attachment_filename,
            attachment_media_type=attachment_media_type, model=model)
    return res["content"]

  security.declarePublic("getMarkerXYZ")
  def getMarkerXYZ(self):
    return "marker-v1"