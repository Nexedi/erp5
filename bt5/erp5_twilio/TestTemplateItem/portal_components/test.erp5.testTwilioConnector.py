# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2024 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
from six.moves.urllib.parse import parse_qs

import responses

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestTwilioConnector(ERP5TypeTestCase):
  """Test Twilio Connector functionality"""

  def afterSetUp(self):
    """Set up test environment"""
    self._document_to_delete_list = []

    self.connector_reference = "test_twilio_connector"
    self.messages_url = "https://api.twilio.com/2010-04-01/Accounts/test_account_sid/Messages.json"
    self.default_to_number = "+33123456789"
    self.default_content_sid = "HX1234567890"
    self.default_content_variables = {"name": "John Doe"}

    # Clean up existing connectors
    for doc in self.portal.portal_catalog(
      portal_type="Twilio Connector",
      reference=self.connector_reference
    ):
      doc.getParentValue().manage_delObjects(ids=[doc.getId(),])

  def _create_connector(self):
    connector = self.portal.portal_web_services.newContent(
      portal_type="Twilio Connector",
      title="Test Twilio Connector",
      reference=self.connector_reference,
      url_string="https://api.twilio.com/2010-04-01",
      client_id="test_account_sid",
      secret_key="test_auth_token",
      from_number="+15551234567"
    )
    connector.validate()
    self.tic()
    self._document_to_delete_list.append(connector)
    return connector

  def beforeTearDown(self):
    self.abort()
    self.tic()
    self.login()

    # Delete all documents
    for doc in self._document_to_delete_list:
      doc.getParentValue().manage_delObjects(ids=[doc.getId(),])
    self.tic()

  def _response_callback(self, message_sid, status="queued"):
    """Callback for successful responses"""
    def _callback(request):
      self.assertEqual(
        'application/x-www-form-urlencoded',
        request.headers['Content-Type'], request.headers)
      body = parse_qs(request.body)
      self.assertIn("To", body)
      self.assertIn("From", body)
      self.assertIn("ContentSid", body)
      # Check WhatsApp formatting
      self.assertTrue(body["To"][0].startswith("whatsapp:"))
      self.assertTrue(body["From"][0].startswith("whatsapp:"))
      return (201, {'content-type': 'application/json'}, json.dumps({
        "sid": message_sid,
        "status": status,
        "messaging_service_sid": None,
        "account_sid": "test_account_sid",
        "to": body["To"][0],
        "from": body["From"][0]
      }))
    return _callback

  def _error_response_callback(self, error_code, error_message, status_code=400):
    """Callback for error responses"""
    def _callback(request):
      return (status_code, {'content-type': 'application/json'}, json.dumps({
        "code": error_code,
        "message": error_message,
        "more_info": "https://www.twilio.com/docs/errors/{}".format(error_code),
        "status": status_code
      }))
    return _callback

  def test_twilio_connector_creation(self):
    """Test property sheets from Twilio Connector"""
    connector = self._create_connector()
    self.assertEqual(connector.getClientId(), 'test_account_sid')
    self.assertEqual(connector.getSecretKey(), 'test_auth_token')
    self.assertEqual(connector.getFromNumber(), '+15551234567')
    self.assertEqual(connector.getReference(), 'test_twilio_connector')

  def test_api_send_whatsapp_message(self):
    """Test API WhatsApp message sending"""
    connector = self._create_connector()

    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.POST,
        self.messages_url,
        self._response_callback("SM123456")
      )
      result = connector.sendWhatsAppMessage(
        self.default_to_number,
        self.default_content_sid,
        self.default_content_variables
      )
      self.assertTrue(result["success"])
      self.assertEqual(result["message_sid"], "SM123456")
      self.assertEqual(result["status"], "queued")

  def test_api_send_whatsapp_message_with_content_variables(self):
    """Test API WhatsApp message sending with content variables"""
    connector = self._create_connector()

    def _request_callback(request):
      self.assertEqual(
        'application/x-www-form-urlencoded', request.headers['Content-Type'],
        request.headers)
      body = parse_qs(request.body)
      self.assertEqual(body["ContentSid"], ["HX1234567890"])
      # Check content variables are properly JSON encoded
      content_vars = json.loads(body["ContentVariables"][0])
      self.assertEqual(content_vars["name"], "John Doe")
      return (
        201, {
          'content-type': 'application/json'
        },
        json.dumps({
          "sid": "SM123456",
          "status": "queued",
          "account_sid": "test_account_sid",
          "to": body["To"][0],
          "from": body["From"][0]
        }))

    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.POST,
        self.messages_url,
        _request_callback,
      )
      result = connector.sendWhatsAppMessage(
        self.default_to_number,
        self.default_content_sid,
        self.default_content_variables
      )
      self.assertTrue(result["success"])
      self.assertEqual(result["message_sid"], "SM123456")

  def test_api_send_whatsapp_message_with_complex_variables(self):
    """Test if complex content variables are serialized properly"""
    connector = self._create_connector()
    complex_variables = {
      "customer": {
        "name": "John Doe",
        "email": "john@example.com"
      },
      "order": {
        "id": "12345",
        "items": ["item1", "item2"]
      }
    }

    def _request_callback(request):
      self.assertEqual(
        'application/x-www-form-urlencoded', request.headers['Content-Type'],
        request.headers)
      body = parse_qs(request.body)
      expected_content_vars = json.dumps(complex_variables)
      self.assertEqual(body["ContentVariables"], [expected_content_vars])
      return (
        201, {
          'content-type': 'application/json'
        },
        json.dumps({
          "sid": "SM123456",
          "status": "queued",
          "account_sid": "test_account_sid"
        }))

    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.POST,
        self.messages_url,
        _request_callback,
      )
      result = connector.sendWhatsAppMessage(
        self.default_to_number,
        self.default_content_sid,
        complex_variables
      )
      self.assertTrue(result["success"])
      self.assertEqual(result["message_sid"], "SM123456")

  def test_api_send_whatsapp_message_unreachable_error(self):
    """Test handling of unreachable WhatsApp recipient"""
    connector = self._create_connector()

    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.POST,
        self.messages_url,
        self._error_response_callback(63003, "The destination phone number is not a WhatsApp user.")
      )
      result = connector.sendWhatsAppMessage(
        self.default_to_number,
        self.default_content_sid,
        self.default_content_variables
      )
      self.assertFalse(result["success"])
      self.assertEqual(result["error_code"], "63003")

  def test_api_send_whatsapp_message_auth_error(self):
    """Test handling of authentication errors"""
    connector = self._create_connector()

    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.POST,
        self.messages_url,
        self._error_response_callback(20003, "Authenticate", 401)
      )
      result = connector.sendWhatsAppMessage(
        self.default_to_number,
        self.default_content_sid,
        self.default_content_variables
      )
      self.assertFalse(result["success"])
      self.assertEqual(result["error_code"], "20003")
      self.assertEqual(result["status_code"], 401)

  def test_api_send_whatsapp_message_invalid_content_sid(self):
    """Test handling of invalid content SID"""
    connector = self._create_connector()

    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.POST,
        self.messages_url,
        self._error_response_callback(20404, "The requested resource was not found")
      )
      result = connector.sendWhatsAppMessage(
        self.default_to_number,
        "HX_INVALID",
        self.default_content_variables
      )
      self.assertFalse(result["success"])
      self.assertEqual(result["error_code"], "20404")