# -*- coding: utf-8 -*-
import requests
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.XMLObject import XMLObject


class OpenaiConnector(XMLObject):
  meta_type = "ERP5 Openai Connector"
  portal_type = "Openai Connector"

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _getBaseUrl(self):
    url = self.getUrlString() or "https://api.openai.com/v1"
    return url.rstrip("/")

  def _buildMessages(self, prompt, message):
    if message:
      return [{"role": "user", "content": message}]
    return [{"role": "user", "content": prompt}]

  security.declarePublic("getModelList")
  def getModelList(self):
    # Return the list of model ids the OpenAI-compatible server exposes.
    api_key = self.getPassword()
    base_url = self._getBaseUrl()
    headers = {"Authorization": "Bearer %s" % api_key}
    resp = requests.get(base_url + "/models", headers=headers, timeout=self.getTimeout(180))
    resp.raise_for_status()
    data = resp.json()
    return [m.get("id") for m in data.get("data", [])]

  security.declarePublic("getResponseWithUsage")
  def getResponseWithUsage(self, prompt=None, attachment_data=None, attachment_filename=None,
                  attachment_media_type="application/pdf", model="gpt-4o", message=None,
                  response_format=None, messages=None, tools=None, tool_choice=None,
                  cert=None, verify=None, timeout=None):
    # Call an OpenAI-compatible Chat Completions endpoint; return
    # {content, tool_calls, model, usage}. When messages (a list) is given it is
    # used verbatim. tools/tool_choice/response_format are forwarded as-is.
    if timeout is None:
      timeout = self.getTimeout(180)
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
        if upload_resp.status_code >= 400:
          raise ValueError("LLM %s error: %s" % (upload_resp.status_code, upload_resp.text[:1000]))
        file_id = upload_resp.json()["id"]
        chat_messages = [{"role": "user",
          "content": [{"type": "text", "text": prompt},
                      {"type": "file", "file": {"file_id": file_id}}]}]
      else:
        chat_messages = self._buildMessages(prompt, message)

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
          requests.delete(base_url + "/files/" + file_id, headers=auth_headers, timeout=self.getTimeout(180), **request_kw)
        except Exception:
          pass
