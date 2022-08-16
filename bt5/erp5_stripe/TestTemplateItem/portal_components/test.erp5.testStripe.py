##############################################################################
#
# Copyright (c) 2002-2022 Nexedi SA and Contributors. All Rights Reserved.
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

import mock
import json
import requests
from urlparse import parse_qs
from DateTime import DateTime
from Products.ERP5Type.Globals import get_request
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestStripePaymentSession(ERP5TypeTestCase):

  def afterSetUp(self):
    self._document_to_delete_list = []
    self.connector_reference = "abc"
    self.method_id = 'Alarm_getStripeConnectorReference'
    self.data = {
      "success_url": "http://success",
      "cancel_url": "http://cancel",
      "line_items": [{
        "price_data": {
          "currency": "eur",
          "unit_amount": "100",
          "product_data": {
            "name": "First Line",
          }
        },
        "quantity": 1
      }, {
        "price_data": {
          "currency": "eur",
          "unit_amount": "200",
          "product_data": {
            "name": "Second Line",
          },
        },
        "quantity": 1
      }]
    }

    custom_skin = self.portal.portal_skins.custom
    if not getattr(custom_skin, self.method_id, None):
      custom_skin.manage_addProduct['PythonScripts'].manage_addPythonScript(
        id=self.method_id
      )

    custom_skin[self.method_id].ZPythonScript_edit(
      '',
      'return "%s"' % self.connector_reference
    )

    for doc in self.portal.portal_catalog(
      portal_type="Stripe Connector",
      reference=self.connector_reference
    ):
      doc.getParentValue().manage_delObjects(ids=[doc.getId(),])

  def _create_connector(self):
    connector = self.portal.portal_web_services.newContent(
      portal_type="Stripe Connector",
      url_string="https://mock:8080",
      description="secret_key",
      reference=self.connector_reference,
    )
    connector.validate()
    self.tic()
    self._document_to_delete_list.append(connector)
    return connector

  def beforeTearDown(self):
    self.abort()
    self.tic()
    self.login('ERP5TypeTestCase')
    for doc in self._document_to_delete_list:
      doc.getParentValue().manage_delObjects(ids=[doc.getId(),])

    custom_skin = self.portal.portal_skins.custom
    if self.method_id in custom_skin.objectIds():
      custom_skin.manage_delObjects([self.method_id])

    self.tic()

  def test_create_stripe_payment_session_and_assign_http_exchange(self):
    stripe_payment_session = self.portal.stripe_payment_session_module.newContent(
      portal_type="Stripe Payment Session")
    self.tic()
    self._document_to_delete_list.append(stripe_payment_session)
    http_exchange = self.portal.system_event_module.newContent(
      portal_type="HTTP Exchange",
      follow_up_value=stripe_payment_session
    )
    self._document_to_delete_list.append(http_exchange)
    self.tic()

    self.assertEqual(
      stripe_payment_session.getUid(),
      http_exchange.getFollowUpUid()
    )
    request = get_request()
    context = self.portal.stripe_payment_session_module[
      stripe_payment_session.getId()
    ]
    request['here'] = context
    line_list = [i.getObjectUid() for i in context.StripePaymentSession_view.listbox.get_value('default',
      render_format='list',
      REQUEST=request) if i.isDataLine()]
    self.assertEqual([http_exchange.getUid(),], line_list)

  def test_stripe_payment_session_workflow(self):
    stripe_payment_session = self.portal.stripe_payment_session_module.newContent(
      portal_type="Stripe Payment Session")
    self.tic()
    self._document_to_delete_list.append(stripe_payment_session)

    self.assertTrue(
      self.portal.portal_workflow.isTransitionPossible(stripe_payment_session, "open")
    )
    self.assertTrue(
      self.portal.portal_workflow.isTransitionPossible(stripe_payment_session, "expire")
    )
    self.assertTrue(
      self.portal.portal_workflow.isTransitionPossible(stripe_payment_session, "complete")
    )

  def test_api_create_session(self):
    connector = self._create_connector()

    def post(url, data, headers, *args, **kw):
      class MockResponse(object):
        def __init__(self, json_data, status_code):
          self.json_data = json_data
          self.status_code = status_code

        def json(self):
          return self.json_data

      self.assertEqual("https://mock:8080/checkout/sessions", url)
      self.assertIn("line_items[0][price_data][unit_amount]", parse_qs(data))
      return MockResponse({
        "id": 123
      }, 200)
  
    with mock.patch.object(requests, "post", side_effect=post):
      response = connector.createSession(data=self.data.copy())
      self.assertEqual(response["id"], 123)

  def test_create_stripe_payment_session_open(self):
    connector = self._create_connector()

    def post(url, data, headers, *args, **kw):
      class MockResponse(object):
        def __init__(self, json_data, status_code):
          self.json_data = json_data
          self.status_code = status_code

        def json(self):
          return self.json_data

      self.assertEqual("https://mock:8080/checkout/sessions", url)
      self.assertIn("line_items[0][price_data][unit_amount]", parse_qs(data))
      return MockResponse({
        "id": "abc123"
      }, 200)

    module = self.portal.stripe_payment_session_module
    with mock.patch.object(requests, "post", side_effect=post):
      stripe_payment_session = module.StripePaymentSessionModule_createStripeSession(
        connector,
        self.data.copy(),
        module.getRelativeUrl(),
        batch_mode=True
      )
      self.tic()
      self._document_to_delete_list.append(stripe_payment_session)
      self.assertEqual(
        "open",
        stripe_payment_session.getValidationState()
      )
      self.assertEqual(
        "abc123",
        stripe_payment_session.getReference()
      )
      self.assertEqual(
        module,
        stripe_payment_session.getCausalityValue()
      )

  def test_alarm_check_stripe_payment_session(self):
    connector = self._create_connector()
    data = self.data.copy()

    def post(url, data, headers, *args, **kw):
      class MockResponse(object):
        def __init__(self, json_data, status_code):
          self.json_data = json_data
          self.status_code = status_code

        def json(self):
          return self.json_data

      parse_qs_data = parse_qs(data)
      self.assertEqual("https://mock:8080/checkout/sessions", url)
      self.assertIn("line_items[0][price_data][unit_amount]", parse_qs_data)

      if "http://completed" in parse_qs_data["success_url"]:
        mock_response = {
          "id": "abc321_completed"
        }
      if "http://expired" in parse_qs_data["success_url"]:
        mock_response = {
          "id": "abc321_expired"
        }
      return MockResponse(mock_response, 200)

    def get(url, headers, *args, **kw):
      class MockResponse(object):
        def __init__(self, json_data, status_code):
          self.json_data = json_data
          self.status_code = status_code

        def json(self):
          return self.json_data

      if "abc321_completed" in url:
        return MockResponse({
          "id": "abc321_completed",
          "status": "complete",
          "object": "checkout.session"
        }, 200)
      if "abc321_expired" in url:
        return MockResponse({
          "id": "abc321_expired",
          "status": "expired",
          "object": "checkout.session"
        }, 200)
      return RuntimeError("Unexpected %s" % url)

    module = self.portal.stripe_payment_session_module
    with mock.patch.object(requests, "post", side_effect=post), \
          mock.patch.object(requests, "get", side_effect=get):

      data["success_url"] = "http://expired"
      first_stripe_payment_session = module.StripePaymentSessionModule_createStripeSession(
        connector, data, module.getRelativeUrl(), batch_mode=True)
      first_stripe_payment_session.setExpirationDate(DateTime() - 1)
      data["success_url"] = "http://completed"

      second_stripe_payment_session = module.StripePaymentSessionModule_createStripeSession(
        connector, data, module.getRelativeUrl(), batch_mode=True)
      second_stripe_payment_session.setExpirationDate(DateTime() - 1)
      self.tic()
      self._document_to_delete_list.append(first_stripe_payment_session)
      self._document_to_delete_list.append(second_stripe_payment_session)
      self.publish('/%s/ERP5Site_receiveStripeWebHook' % self.portal.getId(),
        request_method='POST'
      )
      self.tic()
      self.assertEqual("expired", first_stripe_payment_session.getValidationState())
      self.assertEqual("completed", second_stripe_payment_session.getValidationState())

  def test_update_expiration_date(self):
    connector = self._create_connector()
    data = self.data.copy()

    def post(url, data, headers, *args, **kw):
      class MockResponse(object):
        def __init__(self, json_data, status_code):
          self.json_data = json_data
          self.status_code = status_code

        def json(self):
          return self.json_data

      return MockResponse({
        "id": "test_update_expiration_date"
      }, 200)

    def get(url, headers, *args, **kw):
      class MockResponse(object):
        def __init__(self, json_data, status_code):
          self.json_data = json_data
          self.status_code = status_code

        def json(self):
          return self.json_data

      return MockResponse({
        "id": "test_update_expiration_date",
        "status": "open",
        "object": "checkout.session"
      }, 200)

    module = self.portal.stripe_payment_session_module
    with mock.patch.object(requests, "post", side_effect=post), \
          mock.patch.object(requests, "get", side_effect=get):

      stripe_payment_session = module.StripePaymentSessionModule_createStripeSession(
        connector, data, module.getRelativeUrl(), batch_mode=True)
      stripe_payment_session.setExpirationDate(DateTime() - 1)
      self.tic()
      first_expiration_date = stripe_payment_session.getExpirationDate()
      self._document_to_delete_list.append(stripe_payment_session)
      self.publish('/%s/ERP5Site_receiveStripeWebHook' % self.portal.getId(),
        request_method='POST'
      )
      self.tic()
      second_expiration_date = stripe_payment_session.getExpirationDate()
      self.assertNotEqual(first_expiration_date, second_expiration_date)
      self.assertEqual("open", stripe_payment_session.getValidationState())
      self.publish('/%s/ERP5Site_receiveStripeWebHook' % self.portal.getId(),
        request_method='POST'
      )
      self.tic()
      third_expiration_date = stripe_payment_session.getExpirationDate()
      self.assertEqual(third_expiration_date, second_expiration_date)

  def test_retrieve_stripe_payment_session_status(self):
    connector = self._create_connector()
    session_id = "abc321"
    mock_response = {
      "id": session_id
    }

    def post(url, data, headers, *args, **kw):
      class MockResponse(object):
        def __init__(self, json_data, status_code):
          self.json_data = json_data
          self.status_code = status_code

        def json(self):
          return self.json_data

      self.assertEqual("https://mock:8080/checkout/sessions", url)
      self.assertIn("line_items[0][price_data][unit_amount]", parse_qs(data))
      return MockResponse(mock_response, 200)

    def get(url, headers, *args, **kw):
      class MockResponse(object):
        def __init__(self, json_data, status_code):
          self.json_data = json_data
          self.status_code = status_code

        def json(self):
          return self.json_data

      self.assertEqual("https://mock:8080/checkout/sessions/%s" % session_id, url)
      mock_response["status"] = "expired"
      return MockResponse(mock_response, 200)

    module = self.portal.stripe_payment_session_module
    with mock.patch.object(requests, "post", side_effect=post), \
          mock.patch.object(requests, "get", side_effect=get):
      stripe_payment_session = module.StripePaymentSessionModule_createStripeSession(
        connector,
        self.data.copy(),
        module.getRelativeUrl(),
        batch_mode=True
      )
      self.tic()
      self._document_to_delete_list.append(stripe_payment_session)
      http_exchange = stripe_payment_session.StripePaymentSession_retrieveSession(
        connector, batch_mode=1
      )
      self.assertEqual("HTTP Exchange", http_exchange.getPortalType())
      self.assertEqual("expired", json.loads(http_exchange.getResponse())["status"])