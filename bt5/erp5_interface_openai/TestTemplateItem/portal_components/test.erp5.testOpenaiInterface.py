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

import json

import responses

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestOpenaiConnector(ERP5TypeTestCase):


  def afterSetUp(self):
    self.connector_reference = "test_openai_connector"
    self.base_url = "https://mock.example.com/v1"
    connector = self.portal.portal_catalog.getResultValue(
      portal_type="Openai Connector",
      validation_state='validated',
      reference=self.connector_reference)
    if not connector:
      connector = self.portal.portal_web_services.newContent(
        portal_type="Openai Connector",
        url_string=self.base_url,
        password="secret_api_key",
        reference=self.connector_reference,
      )
      connector.validate()
    self.connector = connector
    self.tic()

  def test_getModelList(self):
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

  def test_getResponseWithUsage_prompt(self):
    connector = self.connector
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        self.base_url + "/chat/completions",
        json={
          "model": "gpt-4o",
          "choices": [{"message": {"content": "Hello there", "tool_calls": []}}],
          "usage": {"prompt_tokens": 3, "completion_tokens": 5, "total_tokens": 8},
        },
        status=200,
      )
      result = connector.getResponseWithUsage(prompt="Hello")
      sent_payload = json.loads(rsps.calls[0].request.body)
      self.assertEqual(
        rsps.calls[0].request.headers["Authorization"], "Bearer secret_api_key")

    self.assertEqual(result["content"], "Hello there")
    self.assertEqual(result["tool_calls"], [])
    self.assertEqual(result["model"], "gpt-4o")
    self.assertEqual(
      result["usage"],
      {"prompt_tokens": 3, "completion_tokens": 5, "total_tokens": 8})
    self.assertEqual(sent_payload["model"], "gpt-4o")
    self.assertEqual(
      sent_payload["messages"], [{"role": "user", "content": "Hello"}])

  def test_getResponseWithUsage_messages_used_verbatim(self):
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
      result = connector.getResponseWithUsage(messages=messages)
      sent_payload = json.loads(rsps.calls[0].request.body)

    self.assertEqual(result["content"], "Hi!")
    self.assertEqual(
      result["usage"],
      {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
    self.assertEqual(sent_payload["messages"], messages)

  def test_getResponseWithUsage_tools_and_tool_choice_forwarded(self):
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
      result = connector.getResponseWithUsage(
        prompt="What's the weather?", tools=tools, tool_choice="auto")
      sent_payload = json.loads(rsps.calls[0].request.body)

    self.assertEqual(result["tool_calls"][0]["function"]["name"], "get_weather")
    self.assertEqual(sent_payload["tools"], tools)
    self.assertEqual(sent_payload["tool_choice"], "auto")

  def test_getResponseWithUsage_attachment_uploads_and_cleans_up_file(self):
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
      result = connector.getResponseWithUsage(
        prompt="Summarize", attachment_data=b"%PDF-1.4 fake",
        attachment_filename="doc.pdf")
      call_count = len(rsps.calls)
      first_call_url = rsps.calls[0].request.url
      last_call_url = rsps.calls[2].request.url

    self.assertEqual(result["content"], "Summary")
    self.assertEqual(call_count, 3)
    self.assertEqual(first_call_url, self.base_url + "/files")
    self.assertEqual(last_call_url, self.base_url + "/files/file-123")

  def test_getResponseWithUsage_http_error_raises(self):
    connector = self.connector
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        self.base_url + "/chat/completions",
        body="Internal error",
        status=500,
      )
      self.assertRaises(
        ValueError, connector.getResponseWithUsage, prompt="Hello")
