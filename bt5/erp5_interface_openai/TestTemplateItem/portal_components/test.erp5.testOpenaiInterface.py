# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2026 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

# The suite covers native OpenAI and Microsoft Foundry, which is Azure OpenAI.

import json

import responses

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestOpenaiConnector(ERP5TypeTestCase):
  """Prove the generic methods of the Openai Connector.

  No test calls the network. The `responses` library answers every call of
  `requests`. No test creates a persistent document.
  """

  def afterSetUp(self):
    self.base_url = "https://mock.example.com/v1"
    self.connector = self.portal.portal_web_services.newContent(
      portal_type="Openai Connector",
      temp_object=True,
      url_string=self.base_url,
      password="secret_api_key",
    )

  def beforeTearDown(self):
    self.abort()

  def test_getModelList(self):
    """Fail when the model list is not read from /v1/models.

    Failure mode: the connector sends no API key, or answers the wrong list.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.GET,
        self.base_url + "/models",
        json={"data": [{"id": "gpt-4o"}, {"id": "gpt-4o-mini"}]},
        status=200,
      )
      model_list = connector.getModelList()
      self.assertEqual(
        rsps.calls[0].request.headers["Authorization"], "Bearer secret_api_key")
    self.assertEqual(model_list, ["gpt-4o", "gpt-4o-mini"])

  def test_createResponse_prompt(self):
    """Fail when one blocking prompt gives the wrong answer shape.

    Failure mode: the caller reads no text, no usage or no background key.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        self.base_url + "/chat/completions",
        json={
          "id": "chatcmpl-1",
          "model": "gpt-4o",
          "choices": [{"message": {"content": "Hello there", "tool_calls": []}}],
          "usage": {"prompt_tokens": 3, "completion_tokens": 5, "total_tokens": 8},
        },
        status=200,
      )
      result = connector.createResponse(prompt="Hello", background=False)
      sent_payload = json.loads(rsps.calls[0].request.body)
      self.assertEqual(
        rsps.calls[0].request.headers["Authorization"], "Bearer secret_api_key")

    self.assertEqual(result["content"], "Hello there")
    self.assertEqual(result["tool_calls"], [])
    self.assertEqual(result["model"], "gpt-4o")
    self.assertEqual(
      result["usage"],
      {"prompt_tokens": 3, "completion_tokens": 5, "total_tokens": 8,
       "cached_tokens": 0})
    self.assertEqual(sent_payload["model"], "gpt-4o")
    self.assertEqual(
      sent_payload["messages"], [{"role": "user", "content": "Hello"}])
    # A Chat Completions answer is complete.
    self.assertEqual(result["id"], "chatcmpl-1")
    self.assertEqual(result["status"], "completed")
    self.assertTrue(result["is_done"])
    self.assertEqual(result["error"], None)
    self.assertEqual(result["file_id"], None)

  def test_createResponse_messages_used_verbatim(self):
    """Fail when the connector changes the message list of the caller.

    Failure mode: the provider reads other messages than the caller sent.
    """
    connector = self.connector
    messages = [
      {"role": "system", "content": "You are a helpful bot."},
      {"role": "user", "content": "Hi"},
    ]
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        self.base_url + "/chat/completions",
        json={
          "model": "gpt-4o",
          "choices": [{"message": {"content": "Hi!"}}],
          "usage": {},
        },
        status=200,
      )
      result = connector.createResponse(messages=messages, background=False)
      sent_payload = json.loads(rsps.calls[0].request.body)

    self.assertEqual(result["content"], "Hi!")
    self.assertEqual(
      result["usage"],
      {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0,
       "cached_tokens": 0})
    self.assertEqual(sent_payload["messages"], messages)

  def test_createResponse_tools_and_tool_choice_forwarded(self):
    """Fail when the tools or the tool choice do not reach the provider.

    Failure mode: the model cannot call one tool of the caller.
    """
    connector = self.connector
    tools = [{"type": "function", "function": {"name": "get_weather"}}]
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        self.base_url + "/chat/completions",
        json={
          "model": "gpt-4o",
          "choices": [{"message": {
            "content": "",
            "tool_calls": [{
              "id": "call_1", "type": "function",
              "function": {"name": "get_weather", "arguments": "{}"},
            }],
          }}],
          "usage": {},
        },
        status=200,
      )
      result = connector.createResponse(
        prompt="What's the weather?", tools=tools, tool_choice="auto",
        background=False)
      sent_payload = json.loads(rsps.calls[0].request.body)

    self.assertEqual(result["tool_calls"][0]["function"]["name"], "get_weather")
    self.assertEqual(sent_payload["tools"], tools)
    self.assertEqual(sent_payload["tool_choice"], "auto")

  def test_createResponse_attachment_uploads_and_cleans_up_file(self):
    """Fail when one blocking call keeps the uploaded file.

    Failure mode: the files of the provider accumulate after each call.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        self.base_url + "/files",
        json={"id": "file-123"},
        status=200,
      )
      rsps.add(
        responses.POST,
        self.base_url + "/chat/completions",
        json={
          "model": "gpt-4o",
          "choices": [{"message": {"content": "Summary"}}],
          "usage": {},
        },
        status=200,
      )
      rsps.add(
        responses.DELETE,
        self.base_url + "/files/file-123",
        status=200,
      )
      result = connector.createResponse(
        prompt="Summarize", attachment_data=b"%PDF-1.4 fake",
        attachment_filename="doc.pdf", background=False)
      call_count = len(rsps.calls)
      first_call_url = rsps.calls[0].request.url
      last_call_url = rsps.calls[2].request.url

    self.assertEqual(result["content"], "Summary")
    self.assertEqual(call_count, 3)
    self.assertEqual(first_call_url, self.base_url + "/files")
    self.assertEqual(last_call_url, self.base_url + "/files/file-123")

  def test_createResponse_http_error_raises(self):
    """Fail when one HTTP error of the provider answers as text.

    Failure mode: the caller stores the error body as one model answer.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        self.base_url + "/chat/completions",
        body="Internal error",
        status=500,
      )
      self.assertRaises(
        ValueError, connector.createResponse, prompt="Hello", background=False)

  RESPONSES_MODEL = "gpt-5.6-luna"

  def _addResponsesAnswer(self, rsps, **kw):
    json_dict = {
      "id": "resp_1",
      "model": self.RESPONSES_MODEL,
      "output": [
        {"type": "message",
         "content": [{"type": "output_text", "text": "Answer"}]},
        {"type": "function_call", "call_id": "call_9",
         "name": "get_weather", "arguments": '{"city": "Paris"}'},
      ],
      "usage": {"input_tokens": 11, "output_tokens": 4, "total_tokens": 15},
    }
    json_dict.update(kw)
    rsps.add(responses.POST, self.base_url + "/responses", json=json_dict,
             status=200)

  def test_tools_with_reasoning_model_use_responses_api(self):
    """Fail when one reasoning model with tools uses Chat Completions.

    Failure mode: the provider refuses the function tools of the request.
    """
    connector = self.connector
    tools = [{"type": "function", "function": {
      "name": "get_weather", "description": "Answer the weather.",
      "parameters": {"type": "object", "properties": {}}}}]
    with responses.RequestsMock() as rsps:
      self._addResponsesAnswer(rsps)
      connector.createResponse(
        prompt="Hi", model=self.RESPONSES_MODEL, tools=tools,
        tool_choice={"type": "function", "function": {"name": "get_weather"}},
        background=False)
      call_url = rsps.calls[0].request.url
      sent_payload = json.loads(rsps.calls[0].request.body)

    self.assertEqual(call_url, self.base_url + "/responses")
    self.assertEqual(sent_payload["input"], [{"role": "user", "content": "Hi"}])
    # The Responses tool shape is flat. The shape has no "function" key.
    self.assertEqual(sent_payload["tools"], [{
      "type": "function", "name": "get_weather",
      "description": "Answer the weather.",
      "parameters": {"type": "object", "properties": {}}}])
    self.assertEqual(
      sent_payload["tool_choice"], {"type": "function", "name": "get_weather"})
    # The blocking call adds no background key.
    self.assertFalse("background" in sent_payload)
    self.assertFalse("store" in sent_payload)

  def test_no_tools_with_reasoning_model_use_chat_completions(self):
    """Fail when one request with no tool leaves Chat Completions.

    Failure mode: a plain request takes the Responses route for no reason.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        self.base_url + "/chat/completions",
        json={
          "model": self.RESPONSES_MODEL,
          "choices": [{"message": {"content": "Plain"}}],
          "usage": {},
        },
        status=200,
      )
      result = connector.createResponse(
        prompt="Hi", model=self.RESPONSES_MODEL, background=False)
      call_url = rsps.calls[0].request.url

    self.assertEqual(call_url, self.base_url + "/chat/completions")
    self.assertEqual(result["content"], "Plain")

  def test_chat_error_that_names_responses_retries_on_responses(self):
    """Fail when one refusal that names /v1/responses is not retried.

    Failure mode: the request fails for one model that needs /v1/responses.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        self.base_url + "/chat/completions",
        body="This model must use /v1/responses",
        status=400,
      )
      self._addResponsesAnswer(rsps)
      result = connector.createResponse(
        prompt="Hi", model="gpt-4o", api_style="chat", background=False)
      call_count = len(rsps.calls)
      second_call_url = rsps.calls[1].request.url

    self.assertEqual(call_count, 2)
    self.assertEqual(second_call_url, self.base_url + "/responses")
    self.assertEqual(result["content"], "Answer")

  def test_responses_answer_maps_content_and_tool_calls(self):
    """Fail when one Responses answer is not mapped to the Chat shape.

    Failure mode: the caller loses the text, the tool calls or the usage.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      self._addResponsesAnswer(rsps)
      result = connector.createResponse(
        prompt="Hi", model=self.RESPONSES_MODEL, api_style="responses",
        background=False)

    self.assertEqual(result["content"], "Answer")
    self.assertEqual(result["model"], self.RESPONSES_MODEL)
    self.assertEqual(len(result["tool_calls"]), 1)
    self.assertEqual(result["tool_calls"][0]["id"], "call_9")
    self.assertEqual(result["tool_calls"][0]["type"], "function")
    self.assertEqual(
      result["tool_calls"][0]["function"],
      {"name": "get_weather", "arguments": '{"city": "Paris"}'})
    self.assertEqual(result["usage"]["prompt_tokens"], 11)
    self.assertEqual(result["usage"]["completion_tokens"], 4)
    self.assertEqual(result["usage"]["total_tokens"], 15)

  def test_reasoning_effort_forwarded_to_both_endpoints(self):
    """Fail when the reasoning effort is lost on one endpoint.

    Failure mode: the model uses its default effort on that endpoint.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        self.base_url + "/chat/completions",
        json={"model": "gpt-4o", "choices": [{"message": {"content": "x"}}],
              "usage": {}},
        status=200,
      )
      connector.createResponse(
        prompt="Hi", model="gpt-4o", reasoning_effort="low", background=False)
      chat_payload = json.loads(rsps.calls[0].request.body)

    with responses.RequestsMock() as rsps:
      self._addResponsesAnswer(rsps)
      connector.createResponse(
        prompt="Hi", model=self.RESPONSES_MODEL, api_style="responses",
        reasoning_effort="high", background=False)
      responses_payload = json.loads(rsps.calls[0].request.body)

    self.assertEqual(chat_payload["reasoning_effort"], "low")
    self.assertEqual(responses_payload["reasoning"], {"effort": "high"})

  def test_prompt_cache_key_forwarded_to_both_endpoints(self):
    """Fail when the prompt cache key is lost on one endpoint.

    Failure mode: the provider cache is not used and each call costs more.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        self.base_url + "/chat/completions",
        json={"model": "gpt-4o", "choices": [{"message": {"content": "x"}}],
              "usage": {}},
        status=200,
      )
      connector.createResponse(
        prompt="Hi", model="gpt-4o", prompt_cache_key="test_cache_key",
        background=False)
      chat_payload = json.loads(rsps.calls[0].request.body)

    with responses.RequestsMock() as rsps:
      self._addResponsesAnswer(rsps)
      connector.createResponse(
        prompt="Hi", model=self.RESPONSES_MODEL, api_style="responses",
        prompt_cache_key="test_cache_key", background=False)
      responses_payload = json.loads(rsps.calls[0].request.body)

    self.assertEqual(chat_payload["prompt_cache_key"], "test_cache_key")
    self.assertEqual(responses_payload["prompt_cache_key"], "test_cache_key")

  def test_cached_token_count_from_both_usage_shapes(self):
    """Fail when the cached token count is lost on one usage shape.

    Failure mode: the token report of the caller shows no cached token.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        self.base_url + "/chat/completions",
        json={
          "model": "gpt-4o",
          "choices": [{"message": {"content": "x"}}],
          "usage": {"prompt_tokens": 20, "completion_tokens": 2,
                    "total_tokens": 22,
                    "prompt_tokens_details": {"cached_tokens": 16}},
        },
        status=200,
      )
      chat_result = connector.createResponse(
        prompt="Hi", model="gpt-4o", background=False)

    with responses.RequestsMock() as rsps:
      self._addResponsesAnswer(rsps, usage={
        "input_tokens": 20, "output_tokens": 2, "total_tokens": 22,
        "input_tokens_details": {"cached_tokens": 16}})
      responses_result = connector.createResponse(
        prompt="Hi", model=self.RESPONSES_MODEL, api_style="responses",
        background=False)

    self.assertEqual(chat_result["usage"]["cached_tokens"], 16)
    self.assertEqual(responses_result["usage"]["cached_tokens"], 16)

  def test_timeout_default_when_property_is_empty(self):
    """Fail when an empty Timeout property gives no default.

    Failure mode: one call waits with no limit, or fails at once.
    """
    self.assertEqual(self.connector._getTimeout(), 180)

  def _addQueuedAnswer(self, rsps, **kw):
    json_dict = {"id": "resp_bg_1", "status": "queued",
                 "model": self.RESPONSES_MODEL}
    json_dict.update(kw)
    rsps.add(responses.POST, self.base_url + "/responses", json=json_dict,
             status=200)

  def test_background_payload_holds_background_and_store(self):
    """Fail when the default call is not one background call.

    Failure mode: the request blocks, or the provider does not store the
    response.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      self._addQueuedAnswer(rsps)
      connector.createResponse(prompt="Hi", model=self.RESPONSES_MODEL)
      call_url = rsps.calls[0].request.url
      sent_payload = json.loads(rsps.calls[0].request.body)

    # Background mode is the default, on /v1/responses.
    self.assertEqual(call_url, self.base_url + "/responses")
    self.assertEqual(sent_payload["background"], True)
    self.assertEqual(sent_payload["store"], True)

  def test_background_start_answers_identifier_and_is_done_false(self):
    """Fail when one background start does not give the identifier.

    Failure mode: the caller cannot read or cancel the response later.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      self._addQueuedAnswer(rsps)
      result = connector.createResponse(prompt="Hi", model=self.RESPONSES_MODEL)

    self.assertEqual(result["id"], "resp_bg_1")
    self.assertEqual(result["status"], "queued")
    self.assertEqual(result["is_done"], False)
    self.assertEqual(result["content"], "")
    self.assertEqual(result["tool_calls"], [])
    self.assertEqual(result["error"], None)
    self.assertEqual(result["file_id"], None)
    self.assertEqual(result["usage"]["total_tokens"], 0)

  def test_chat_api_style_with_background_raises_value_error(self):
    """Fail when Chat Completions accepts one background request.

    Failure mode: the connector sends one request that the endpoint cannot
    run.
    """
    connector = self.connector
    with responses.RequestsMock():
      self.assertRaises(
        ValueError, connector.createResponse, prompt="Hi", api_style="chat",
        background=True)

  def test_retrieveResponse_reads_the_response_path(self):
    """Fail when retrieveResponse reads the wrong path.

    Failure mode: the caller never sees the state of the response.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.GET,
        self.base_url + "/responses/resp_bg_1",
        json={"id": "resp_bg_1", "status": "in_progress",
              "model": self.RESPONSES_MODEL},
        status=200,
      )
      result = connector.retrieveResponse("resp_bg_1")
      call_url = rsps.calls[0].request.url
      self.assertEqual(
        rsps.calls[0].request.headers["Authorization"], "Bearer secret_api_key")

    self.assertEqual(call_url, self.base_url + "/responses/resp_bg_1")
    self.assertEqual(result["id"], "resp_bg_1")
    self.assertEqual(result["status"], "in_progress")
    self.assertEqual(result["is_done"], False)

  def test_retrieveResponse_http_error_raises(self):
    """Fail when one failed read answers as one result.

    Failure mode: the caller ends one line that is still running.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.GET,
        self.base_url + "/responses/resp_bg_1",
        body="Not found",
        status=404,
      )
      self.assertRaises(
        ValueError, connector.retrieveResponse, "resp_bg_1")

  def test_each_status_value_maps_to_the_right_shape(self):
    """Fail when one of the six status values gives the wrong shape.

    Failure mode: the caller ends one running response, or waits for one ended
    response.
    """
    connector = self.connector
    body_by_status = {
      "queued": {},
      "in_progress": {},
      "completed": {
        "output": [{"type": "message",
                    "content": [{"type": "output_text", "text": "Answer"}]}],
        "usage": {"input_tokens": 11, "output_tokens": 4,
                  "total_tokens": 15},
      },
      "failed": {"error": {"code": "server_error", "message": "boom"}},
      "incomplete": {"incomplete_details": {"reason": "max_output_tokens"}},
      "cancelled": {"usage": {"input_tokens": 7, "output_tokens": 1,
                              "total_tokens": 8}},
    }
    expected_is_done_dict = {
      "queued": False, "in_progress": False, "completed": True,
      "failed": True, "incomplete": True, "cancelled": True,
    }
    result_dict = {}
    for status in sorted(body_by_status):
      body = {"id": "resp_bg_1", "status": status,
              "model": self.RESPONSES_MODEL}
      body.update(body_by_status[status])
      with responses.RequestsMock() as rsps:
        rsps.add(
          responses.GET,
          self.base_url + "/responses/resp_bg_1",
          json=body,
          status=200,
        )
        result_dict[status] = connector.retrieveResponse("resp_bg_1")

    for status in sorted(body_by_status):
      result = result_dict[status]
      self.assertEqual(result["status"], status)
      self.assertEqual(result["is_done"], expected_is_done_dict[status])
      self.assertEqual(result["id"], "resp_bg_1")
      self.assertEqual(result["model"], self.RESPONSES_MODEL)

    # A response that is not done holds no text and no error.
    for status in ("queued", "in_progress"):
      self.assertEqual(result_dict[status]["content"], "")
      self.assertEqual(result_dict[status]["error"], None)

    # A completed response holds the text and the token count.
    self.assertEqual(result_dict["completed"]["content"], "Answer")
    self.assertEqual(result_dict["completed"]["error"], None)
    self.assertEqual(
      result_dict["completed"]["usage"],
      {"prompt_tokens": 11, "completion_tokens": 4, "total_tokens": 15,
       "cached_tokens": 0})

    # A failed response holds the error of the provider.
    self.assertEqual(
      result_dict["failed"]["error"],
      {"code": "server_error", "message": "boom"})
    self.assertEqual(result_dict["failed"]["content"], "")

    # An incomplete response holds the reason under the code "incomplete".
    self.assertEqual(
      result_dict["incomplete"]["error"],
      {"code": "incomplete", "message": "max_output_tokens"})

    # A cancelled response holds the tokens that the provider billed.
    self.assertEqual(result_dict["cancelled"]["error"], None)
    self.assertEqual(result_dict["cancelled"]["usage"]["total_tokens"], 8)

  def test_retrieveResponse_deletes_the_file_when_the_response_is_done(self):
    """Fail when one ended response keeps the uploaded file.

    Failure mode: the files of the provider accumulate after each run.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.GET,
        self.base_url + "/responses/resp_bg_1",
        json={"id": "resp_bg_1", "status": "completed",
              "model": self.RESPONSES_MODEL,
              "output": [{"type": "message", "content": [
                {"type": "output_text", "text": "Summary"}]}]},
        status=200,
      )
      rsps.add(
        responses.DELETE,
        self.base_url + "/files/file-123",
        status=200,
      )
      result = connector.retrieveResponse("resp_bg_1", file_id="file-123")
      call_count = len(rsps.calls)
      last_call_url = rsps.calls[1].request.url

    self.assertEqual(result["content"], "Summary")
    self.assertEqual(result["file_id"], "file-123")
    self.assertEqual(call_count, 2)
    self.assertEqual(last_call_url, self.base_url + "/files/file-123")

  def test_retrieveResponse_keeps_the_file_while_the_response_runs(self):
    """Fail when the file is deleted while the response runs.

    Failure mode: the provider cannot read the file and the generation breaks.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.GET,
        self.base_url + "/responses/resp_bg_1",
        json={"id": "resp_bg_1", "status": "in_progress",
              "model": self.RESPONSES_MODEL},
        status=200,
      )
      result = connector.retrieveResponse("resp_bg_1", file_id="file-123")
      call_count = len(rsps.calls)

    self.assertEqual(result["is_done"], False)
    self.assertEqual(call_count, 1)

  def test_background_attachment_keeps_the_file_and_answers_the_file_id(self):
    """Fail when one background start deletes the file.

    Failure mode: the provider cannot read the file of the running response.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        self.base_url + "/files",
        json={"id": "file-123"},
        status=200,
      )
      self._addQueuedAnswer(rsps)
      result = connector.createResponse(
        prompt="Summarize", attachment_data=b"%PDF-1.4 fake",
        attachment_filename="doc.pdf", model=self.RESPONSES_MODEL)
      call_count = len(rsps.calls)
      first_call_url = rsps.calls[0].request.url
      second_call_url = rsps.calls[1].request.url

    # Two calls only. The connector sends no DELETE.
    self.assertEqual(call_count, 2)
    self.assertEqual(first_call_url, self.base_url + "/files")
    self.assertEqual(second_call_url, self.base_url + "/responses")
    self.assertEqual(result["file_id"], "file-123")
    self.assertEqual(result["is_done"], False)

  def test_cancelResponse_calls_the_cancel_path(self):
    """Fail when cancelResponse does not call the cancel path.

    Failure mode: the provider continues the work and bills it.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        self.base_url + "/responses/resp_bg_1/cancel",
        json={"id": "resp_bg_1", "status": "cancelled",
              "model": self.RESPONSES_MODEL,
              "usage": {"input_tokens": 7, "output_tokens": 1,
                        "total_tokens": 8}},
        status=200,
      )
      result = connector.cancelResponse("resp_bg_1")
      call_count = len(rsps.calls)
      call_url = rsps.calls[0].request.url
      call_body = rsps.calls[0].request.body

    self.assertEqual(call_count, 1)
    self.assertEqual(call_url, self.base_url + "/responses/resp_bg_1/cancel")
    # The cancel call holds no body.
    self.assertEqual(call_body, None)
    self.assertEqual(result["status"], "cancelled")
    self.assertEqual(result["is_done"], True)
    self.assertEqual(result["id"], "resp_bg_1")
    # The provider bills the tokens that it generated before the stop.
    self.assertEqual(result["usage"]["total_tokens"], 8)

  def test_cancelResponse_deletes_the_file(self):
    """Fail when one cancel keeps the uploaded file.

    Failure mode: the files of the provider accumulate after each cancel.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        self.base_url + "/responses/resp_bg_1/cancel",
        json={"id": "resp_bg_1", "status": "cancelled",
              "model": self.RESPONSES_MODEL},
        status=200,
      )
      rsps.add(
        responses.DELETE,
        self.base_url + "/files/file-123",
        status=200,
      )
      connector.cancelResponse("resp_bg_1", file_id="file-123")
      call_count = len(rsps.calls)
      last_call_url = rsps.calls[1].request.url

    self.assertEqual(call_count, 2)
    self.assertEqual(last_call_url, self.base_url + "/files/file-123")

  def test_response_id_with_a_path_character_raises(self):
    """Fail when one identifier with a path character is accepted.

    Failure mode: the API key of the provider is sent to another path.
    """
    connector = self.connector
    bad_id_list = ("../files?x=", "resp/1", "resp?x=1", "resp#1", "")
    for bad_id in bad_id_list:
      with responses.RequestsMock() as rsps:
        self.assertRaises(ValueError, connector.retrieveResponse, bad_id)
        self.assertEqual(len(rsps.calls), 0)
      with responses.RequestsMock() as rsps:
        self.assertRaises(ValueError, connector.cancelResponse, bad_id)
        self.assertEqual(len(rsps.calls), 0)

  AZURE_BASE_URL = "https://mock-resource.services.ai.azure.com/openai/v1"

  AZURE_URL_TUPLE = (
    "https://mock-resource.services.ai.azure.com/openai/v1",
    "https://x.openai.azure.com",
    "https://x.openai.azure.com:443/openai/v1",
    "https://x.cognitiveservices.azure.com/openai/v1",
    "https://x.services.ai.azure.us/openai/v1",
    "https://x.openai.azure.cn/openai/v1",
  )

  # WARNING: these servers refuse the upload when they get the Azure purpose.
  NON_AZURE_URL_TUPLE = (
    "https://api.openai.com/v1",
    "https://vllm.westeurope.cloudapp.azure.com/v1",
    "https://proxy.example.com/relay/x.azure.com/v1",
    "http://127.0.0.1:8080/v1",
  )

  def _useProviderUrl(self, url):
    connector = self.connector
    setUrlString = getattr(connector, "setUrlString", None)
    if setUrlString is None:
      # The offline harness holds no property sheet. Write the reader method.
      connector.getUrlString = lambda: url
    else:
      setUrlString(url)

  def _readUploadPurpose(self, request):
    body = request.body
    if not isinstance(body, bytes):
      body = body.encode("utf-8")
    marker = b'name="purpose"'
    index = body.find(marker)
    if index < 0:
      return None
    value = body[index + len(marker):].split(b"\r\n\r\n", 1)[1]
    return value.split(b"\r\n", 1)[0].decode("ascii")

  def _addFileAnswer(self, rsps, base_url, file_id="file-provider-1"):
    rsps.add(responses.POST, base_url + "/files", json={"id": file_id},
             status=200)

  def _addChatAnswer(self, rsps, base_url, model="gpt-4o"):
    rsps.add(
      responses.POST, base_url + "/chat/completions",
      json={"model": model, "choices": [{"message": {"content": "Answer"}}],
            "usage": {}},
      status=200)

  def _addPlainResponsesAnswer(self, rsps, base_url, model="gpt-4o"):
    rsps.add(
      responses.POST, base_url + "/responses",
      json={"id": "resp_provider_1", "model": model, "status": "completed",
            "output": [{"type": "message", "content": [
              {"type": "output_text", "text": "Answer"}]}],
            "usage": {}},
      status=200)

  def test_getHostName_drops_the_scheme_the_path_the_user_and_the_port(self):
    """Fail when the host name holds more than the host.

    Failure mode: the provider detection reads the wrong text.
    """
    connector = self.connector
    self.assertEqual(
      connector._getHostName("https://x.openai.azure.com:443/openai/v1"),
      "x.openai.azure.com")
    self.assertEqual(
      connector._getHostName("http://user@127.0.0.1:8080/v1"), "127.0.0.1")
    self.assertEqual(
      connector._getHostName("https://api.openai.com/v1"), "api.openai.com")

  def test_azure_host_names_are_detected(self):
    """Fail when one Azure URL is not detected as Azure.

    Failure mode: the upload purpose is user_data and Azure refuses the
    upload.
    """
    connector = self.connector
    for url in self.AZURE_URL_TUPLE:
      self._useProviderUrl(url)
      self.assertTrue(
        connector._isAzureProvider(),
        "The connector reads %s as one provider that is not Azure. The "
        "upload purpose then becomes user_data, and Microsoft Foundry "
        "refuses the upload." % (url, ))

  def test_host_names_that_are_not_azure_are_not_detected(self):
    """Fail when one URL that is not Azure is detected as Azure.

    Failure mode: the upload purpose is assistants and the server refuses it.
    """
    connector = self.connector
    for url in self.NON_AZURE_URL_TUPLE:
      self._useProviderUrl(url)
      self.assertFalse(
        connector._isAzureProvider(),
        "The connector reads %s as one Azure provider. The upload purpose "
        "then becomes assistants, and one server that is not Azure refuses "
        "the upload." % (url, ))

  def test_upload_purpose_is_assistants_on_azure_messages_route(self):
    """Fail when the messages route sends user_data to Azure.

    Failure mode: Azure refuses the upload.
    """
    connector = self.connector
    self._useProviderUrl(self.AZURE_BASE_URL)
    with responses.RequestsMock() as rsps:
      self._addFileAnswer(rsps, self.AZURE_BASE_URL)
      self._addPlainResponsesAnswer(rsps, self.AZURE_BASE_URL)
      connector.createResponse(
        messages=[{"role": "user", "content": "Read the file."}],
        attachment_data=b"%PDF-1.4 fake", attachment_filename="doc.pdf",
        background=False)
      purpose = self._readUploadPurpose(rsps.calls[0].request)

    self.assertEqual(
      purpose, "assistants",
      "The messages route sends the upload purpose %r to Microsoft Foundry. "
      "Microsoft Foundry needs assistants." % (purpose, ))

  def test_upload_purpose_is_user_data_on_openai_messages_route(self):
    """Fail when the messages route sends assistants to native OpenAI.

    Failure mode: native OpenAI refuses the file input.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      self._addFileAnswer(rsps, self.base_url)
      self._addChatAnswer(rsps, self.base_url)
      connector.createResponse(
        messages=[{"role": "user", "content": "Read the file."}],
        attachment_data=b"%PDF-1.4 fake", attachment_filename="doc.pdf",
        background=False)
      purpose = self._readUploadPurpose(rsps.calls[0].request)

    self.assertEqual(
      purpose, "user_data",
      "The messages route sends the upload purpose %r to native OpenAI. "
      "Native OpenAI needs user_data." % (purpose, ))

  def test_upload_purpose_is_assistants_on_azure_attachment_route(self):
    """Fail when the attachment route sends user_data to Azure.

    Failure mode: Azure refuses the upload.
    """
    connector = self.connector
    self._useProviderUrl(self.AZURE_BASE_URL)
    with responses.RequestsMock() as rsps:
      self._addFileAnswer(rsps, self.AZURE_BASE_URL)
      self._addPlainResponsesAnswer(rsps, self.AZURE_BASE_URL)
      rsps.add(responses.DELETE,
               self.AZURE_BASE_URL + "/files/file-provider-1", status=200)
      connector.createResponse(
        prompt="Read the file.", attachment_data=b"%PDF-1.4 fake",
        attachment_filename="doc.pdf", background=False)
      purpose = self._readUploadPurpose(rsps.calls[0].request)

    self.assertEqual(
      purpose, "assistants",
      "The attachment_data route sends the upload purpose %r to Microsoft "
      "Foundry. Microsoft Foundry needs assistants." % (purpose, ))

  def test_upload_purpose_is_user_data_on_openai_attachment_route(self):
    """Fail when the attachment route sends assistants to native OpenAI.

    Failure mode: native OpenAI refuses the file input.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      self._addFileAnswer(rsps, self.base_url)
      self._addChatAnswer(rsps, self.base_url)
      rsps.add(responses.DELETE,
               self.base_url + "/files/file-provider-1", status=200)
      connector.createResponse(
        prompt="Read the file.", attachment_data=b"%PDF-1.4 fake",
        attachment_filename="doc.pdf", background=False)
      purpose = self._readUploadPurpose(rsps.calls[0].request)

    self.assertEqual(
      purpose, "user_data",
      "The attachment_data route sends the upload purpose %r to native "
      "OpenAI. Native OpenAI needs user_data." % (purpose, ))

  JSON_SCHEMA_FORMAT = {
    "type": "json_schema",
    "json_schema": {
      "name": "test_answer_schema",
      "schema": {"type": "object", "properties": {}},
      "strict": True,
    },
  }

  def test_json_schema_becomes_flat_under_the_text_format(self):
    """Fail when /v1/responses gets the nested json_schema shape.

    Failure mode: the provider ignores the schema of the caller.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      self._addPlainResponsesAnswer(rsps, self.base_url)
      connector.createResponse(
        prompt="Hi", api_style="responses", background=False,
        response_format=self.JSON_SCHEMA_FORMAT)
      sent_payload = json.loads(rsps.calls[0].request.body)

    text_format = sent_payload["text"]["format"]
    self.assertEqual(
      text_format,
      {"type": "json_schema", "name": "test_answer_schema",
       "schema": {"type": "object", "properties": {}}, "strict": True},
      "The /v1/responses payload carries the format %r. The provider needs "
      "the flat shape." % (text_format, ))
    # The caller must read its own value unchanged.
    self.assertEqual(
      self.JSON_SCHEMA_FORMAT["json_schema"]["name"], "test_answer_schema")

  def test_chat_completions_keeps_the_nested_response_format(self):
    """Fail when Chat Completions gets the flat json_schema shape.

    Failure mode: the native OpenAI path loses the schema of the caller.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      self._addChatAnswer(rsps, self.base_url)
      connector.createResponse(
        prompt="Hi", api_style="chat", background=False,
        response_format=self.JSON_SCHEMA_FORMAT)
      sent_payload = json.loads(rsps.calls[0].request.body)

    self.assertEqual(sent_payload["response_format"], self.JSON_SCHEMA_FORMAT)
    self.assertFalse("text" in sent_payload)

  def test_other_response_format_values_pass_unchanged(self):
    """Fail when one format that is not json_schema is changed.

    Failure mode: the provider gets another format than the caller sent.
    """
    connector = self.connector
    self.assertEqual(
      connector._buildResponsesTextFormat({"type": "json_object"}),
      {"type": "json_object"})
    self.assertEqual(connector._buildResponsesTextFormat("text"), "text")
    self.assertEqual(connector._buildResponsesTextFormat(None), None)

  def test_json_schema_without_an_inner_map_passes_unchanged(self):
    """Fail when one incomplete json_schema value raises or is changed.

    Failure mode: one bad value of the caller stops the request.
    """
    connector = self.connector
    for response_format in (
        {"type": "json_schema"},
        {"type": "json_schema", "json_schema": None},
        {"type": "json_schema", "json_schema": "test_answer_schema"}):
      self.assertEqual(
        connector._buildResponsesTextFormat(response_format), response_format)

  def test_azure_with_a_file_uses_the_responses_endpoint(self):
    """Fail when Azure with one file uses Chat Completions.

    Failure mode: Azure refuses the file input.
    """
    connector = self.connector
    self._useProviderUrl(self.AZURE_BASE_URL)
    with responses.RequestsMock() as rsps:
      self._addPlainResponsesAnswer(rsps, self.AZURE_BASE_URL)
      connector.createResponse(
        messages=[{"role": "user", "content": "Read the file."}],
        file_id="file-provider-1", background=False)
      call_url = rsps.calls[0].request.url

    self.assertEqual(call_url, self.AZURE_BASE_URL + "/responses")

  def test_openai_with_a_file_uses_the_chat_endpoint(self):
    """Fail when native OpenAI with one file leaves Chat Completions.

    Failure mode: the native OpenAI path changes with no request of the
    caller.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      self._addChatAnswer(rsps, self.base_url)
      connector.createResponse(
        messages=[{"role": "user", "content": "Read the file."}],
        file_id="file-provider-1", background=False)
      call_url = rsps.calls[0].request.url

    self.assertEqual(
      call_url, self.base_url + "/chat/completions",
      "Native OpenAI with one file reaches %s. The production path is "
      "/v1/chat/completions." % (call_url, ))

  def test_an_explicit_api_style_wins_on_both_providers(self):
    """Fail when the provider overrides one explicit api_style.

    Failure mode: the caller cannot choose the endpoint.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      self._addPlainResponsesAnswer(rsps, self.base_url)
      connector.createResponse(
        messages=[{"role": "user", "content": "Read the file."}],
        file_id="file-provider-1", api_style="responses", background=False)
      openai_url = rsps.calls[0].request.url

    self._useProviderUrl(self.AZURE_BASE_URL)
    with responses.RequestsMock() as rsps:
      self._addChatAnswer(rsps, self.AZURE_BASE_URL)
      connector.createResponse(
        messages=[{"role": "user", "content": "Read the file."}],
        file_id="file-provider-1", api_style="chat", background=False)
      azure_url = rsps.calls[0].request.url

    self.assertEqual(openai_url, self.base_url + "/responses")
    self.assertEqual(azure_url, self.AZURE_BASE_URL + "/chat/completions")

  def test_background_forces_the_responses_endpoint_on_both_providers(self):
    """Fail when one background call leaves /v1/responses.

    Failure mode: the background request goes to an endpoint that cannot run
    it.
    """
    connector = self.connector
    with responses.RequestsMock() as rsps:
      self._addQueuedAnswer(rsps)
      connector.createResponse(prompt="Hi", model=self.RESPONSES_MODEL)
      openai_url = rsps.calls[0].request.url
      openai_payload = json.loads(rsps.calls[0].request.body)

    self._useProviderUrl(self.AZURE_BASE_URL)
    with responses.RequestsMock() as rsps:
      rsps.add(responses.POST, self.AZURE_BASE_URL + "/responses",
               json={"id": "resp_bg_1", "status": "queued",
                     "model": self.RESPONSES_MODEL}, status=200)
      connector.createResponse(prompt="Hi", model=self.RESPONSES_MODEL)
      azure_url = rsps.calls[0].request.url
      azure_payload = json.loads(rsps.calls[0].request.body)

    self.assertEqual(openai_url, self.base_url + "/responses")
    self.assertEqual(azure_url, self.AZURE_BASE_URL + "/responses")
    self.assertEqual(openai_payload["background"], True)
    self.assertEqual(azure_payload["background"], True)
    self.assertEqual(openai_payload["store"], True)
    self.assertEqual(azure_payload["store"], True)
