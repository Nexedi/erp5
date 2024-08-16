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

import json
from io import BytesIO
from six.moves.urllib.parse import parse_qs

import requests
import responses

from DateTime import DateTime
from Products.ERP5Type.Globals import get_request
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestStripePaymentSession(ERP5TypeTestCase):

  def afterSetUp(self):
    self._document_to_delete_list = []
    self._session_to_delete = set()

    self.connector_reference = "abc"
    self.session_url = "https://mock:8080/checkout/sessions"
    self.default_item_line = {
      "price_data": {
        "currency": "eur",
        "unit_amount": "100",
        "product_data": {
          "name": "First Line",
        }
      },
      "quantity": 1
    }
    self.data = {
      "success_url": "http://success",
      "cancel_url": "http://cancel",
      "line_items": [self.default_item_line, {
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

    for doc in self.portal.portal_catalog(
      portal_type="Stripe Connector",
      reference=self.connector_reference
    ):
      doc.getParentValue().manage_delObjects(ids=[doc.getId(),])

  def _create_connector(self):
    connector = self.portal.portal_web_services.newContent(
      portal_type="Stripe Connector",
      url_string="https://mock:8080",
      password="secret_key",
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
    for session in self.portal.stripe_payment_session_module.objectValues():
      session.setReference("disabled_" + (session.getReference() or "IGNORE"))
      if session.getValidationState() == "open":
        session.expire()

    self.tic()

    if self._session_to_delete:
      for session in [s.getObject() for s in self.portal.stripe_payment_session_module.searchFolder(
        reference=self._session_to_delete)]:
        if session not in self._document_to_delete_list:
          self._document_to_delete_list.append(session)

    for doc in self._document_to_delete_list:
      if doc.getPortalType() == "Stripe Payment Session":
        for obj in doc.getFollowUpRelatedValueList(portal_type="HTTP Exchange"):
          if obj not in self._document_to_delete_list:
            self._document_to_delete_list.append(obj)

    for doc in self._document_to_delete_list:
      doc.getParentValue().manage_delObjects(ids=[doc.getId(),])
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

  def _get_response_callback(self, session_id):
    """Callback for responses
    """
    self._session_to_delete.add(session_id)

    def _callback(request):
      url = request.url
      if session_id in ("abc321_completed", "abc321_webhook"):
        return (200, {'content-type': 'application/json'}, json.dumps({
          "id": session_id,
          "status": "complete",
          "payment_status": "paid",
          "object": "checkout.session"
        }))
      if session_id == "abc321_expired":
        return (200, {'content-type': 'application/json'}, json.dumps({
          "id": session_id,
          "status": "expired",
          "object": "checkout.session"
        }))
      if session_id == "abc321":
        return (200, {'content-type': 'application/json'}, json.dumps({
          "id": session_id,
          "status": "expired",
          "object": "checkout.session"
        }))
      if session_id == "not_found":
        return (404, {'content-type': 'application/json'}, json.dumps({
          "error": {
            "message": "Invalid checkout.session id: not_found",
            "type": "invalid_request_error"
          }
        }))
      return RuntimeError("Unexpected %s" % url)
    return _callback

  def _response_callback(self, session_id, status="open"):
    """Callback for responses
    """
    def _callback(request):
      self.assertEqual(
        'application/x-www-form-urlencoded',
        request.headers['Content-Type'], request.headers)
      body = parse_qs(request.body)
      self.assertIn("line_items[0][price_data][unit_amount]", body)
      self.assertIn("line_items[1][price_data][unit_amount]", body)
      return (200, {'content-type': 'application/json'}, json.dumps({
        "id": session_id,
        "status": status,
        "object": "checkout.session",
        "url": "https://stripe.url"
      }))
    return _callback

  def test_api_create_session(self):
    connector = self._create_connector()

    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.POST,
        self.session_url,
        self._response_callback("123")
      )
      response = connector.createSession(data=self.data.copy())
      self.assertEqual(response["id"], "123")

  def test_api_create_session_with_metadata(self):
    connector = self._create_connector()

    def _request_callback(request):
      self.assertEqual(
        'application/x-www-form-urlencoded', request.headers['Content-Type'],
        request.headers)
      body = parse_qs(request.body)
      self.assertEqual(
        body, {
          "success_url": ["http://success"],
          "cancel_url": ["http://cancel"],
          "line_items[0][price_data][currency]": ["eur"],
          "line_items[0][price_data][unit_amount]": ["100"],
          "line_items[0][price_data][product_data][name]": ["First Line"],
          "line_items[0][quantity]": ["1"],
          "metadata[key]": ["value"],
          "mode": ["payment"],
        })
      return (
        200, {
          'content-type': 'application/json'
        },
        json.dumps(
          {
            "id": "123",
            "status": "open",
            "object": "checkout.session"
          }))

    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.POST,
        self.session_url,
        _request_callback,
      )
      response = connector.createSession(
        data={
          "success_url": "http://success",
          "cancel_url": "http://cancel",
          "line_items": [
            self.default_item_line
          ],
          "metadata": {
            "key": "value",
          },
          "mode": "payment"
        })
      self.assertEqual(response["id"], "123")

  def test_api_create_session_with_any_hash(self):
    """ Test if dicts and lists are serialized properly
    """
    connector = self._create_connector()

    def _request_callback(request):
      self.assertEqual(
        'application/x-www-form-urlencoded', request.headers['Content-Type'],
        request.headers)
      body = parse_qs(request.body)
      self.assertEqual(
        body, {
          "automatic_tax[enabled]": ['true'],
          "automatic_tax[status]": ['complete'],
          "success_url": ["http://success"],
          "cancel_url": ["http://cancel"],
          'custom_text[shipping_text][message]': ['Rue XV'],
          'custom_text[submit][message]': ['Rue XV'],
          'customer_details[address]': ['Rue XV'],
          'customer_details[email]': ['text@text.com'],
          'customer_details[name]': ['My name'],
          'customer_details[phone]': ['2199909'],
          'customer_details[tax_exempt]': ['tax'],
          'customer_details[tax_ids][0][type]': ['eu_vat'],
          'customer_details[tax_ids][0][value]': ['33'],
          'customer_details[tax_ids][1][type]': ['br_cnpj'],
          'customer_details[tax_ids][1][value]': ['33'],
          "line_items[0][price_data][currency]": ["eur"],
          "line_items[0][price_data][unit_amount]": ["100"],
          "line_items[0][price_data][product_data][name]": ["First Line"],
          "line_items[0][quantity]": ["1"],
          "metadata[key]": ["value"],
          "metadata[key1]": ["value1"],
          "metadata[key2]": ["value2"],
          "mode": ["payment"],
          "payment_method_options[acss_debit][current]": ['usd']
        })
      return (
        200, {
          'content-type': 'application/json'
        },
        json.dumps(
          {
            "id": "123",
            "status": "open",
            "object": "checkout.session"
          }))

    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.POST,
        self.session_url,
        _request_callback,
      )
      response = connector.createSession(
        data={
          "success_url": "http://success",
          "cancel_url": "http://cancel",
          "line_items": [
            self.default_item_line
          ],
          "metadata": {
            "key": "value",
            "key1": "value1",
            "key2": "value2",
          },
          "automatic_tax": {
            "enabled": "true",
            "status": "complete"
          },
          "custom_text": {
            "shipping_text": {
            "message": "Rue XV",
            },
            "submit": {
              "message": "Rue XV",
            }
          },
          "customer_details": {
            "address": "Rue XV",
            "email": "text@text.com",
            "name": "My name",
            "phone": "2199909",
            "tax_exempt": "tax",
            "tax_ids": [{
              "type": "eu_vat",
              "value": "33"
            }, {
              "type": "br_cnpj",
              "value": "33"
            }]
          },
          "payment_method_options": {
            "acss_debit": {
              "current": "usd"
            }
          },
          "mode": "payment"
        })
      self.assertEqual(response["id"], "123")

  def test_create_stripe_payment_session_open(self):
    connector = self._create_connector()

    module = self.portal.stripe_payment_session_module
    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.POST,
        self.session_url,
        self._response_callback("abc123")
      )
      module.StripePaymentSessionModule_createStripeSession(
        connector,
        self.data.copy(),
        module.getRelativeUrl(),
      )
      self.tic()
      stripe_payment_session = self.portal.portal_catalog.getResultValue(
        portal_type="Stripe Payment Session",
        reference="abc123"
      )
      self.assertEqual(connector, stripe_payment_session.getSourceValue())
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

    module = self.portal.stripe_payment_session_module
    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.POST,
        self.session_url,
        self._response_callback("abc321_expired")
      )
      module.StripePaymentSessionModule_createStripeSession(
        connector, data, module.getRelativeUrl())
      self.tic()
      first_stripe_payment_session = self.portal.portal_catalog.getResultValue(
        portal_type="Stripe Payment Session",
        reference="abc321_expired"
      )
      first_stripe_payment_session.setExpirationDate(DateTime() - 1)
      self.tic()

    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.POST,
        self.session_url,
        self._response_callback("abc321_completed")
      )
      module.StripePaymentSessionModule_createStripeSession(
        connector, data, module.getRelativeUrl())
      self.tic()
      second_stripe_payment_session = self.portal.portal_catalog.getResultValue(
        portal_type="Stripe Payment Session",
        reference="abc321_completed"
      )
      second_stripe_payment_session.setExpirationDate(DateTime() - 1)
      self.tic()

    self._document_to_delete_list.append(first_stripe_payment_session)
    self._document_to_delete_list.append(second_stripe_payment_session)

    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.GET,
        "https://mock:8080/checkout/sessions/abc321_expired",
        self._get_response_callback("abc321_expired")
      )
      rsps.add_callback(
        responses.GET,
        "https://mock:8080/checkout/sessions/abc321_completed",
        self._get_response_callback("abc321_completed")
      )
      ret = self.publish(
        "%s/ERP5Site_receiveStripeWebHook" % self.portal.getPath(),
        stdin=BytesIO(
          json.dumps({
            "url": "https://stripe.url",
            "id": "evt_%s" % "abc321_expired",
            "object": "event",
            "data": {
              "object": {
                "id": "abc321_expired",
                "status": "expired",
                "payment_status": "unpaid",
                "object": "checkout.session"
              }
            }
          }).encode()
        ),
        request_method="POST",
        env={'CONTENT_TYPE': 'application/json'},
        handle_errors=False)
      self.assertEqual(200, ret.getStatus())
      self.tic()
      self.assertEqual("expired", first_stripe_payment_session.getValidationState())
      self.assertEqual("completed", second_stripe_payment_session.getValidationState())

    self.tic()
    self.assertEqual(
      None,
      first_stripe_payment_session.StripePaymentSession_checkStripeSessionOpen()
    )
    self.assertEqual(
      None,
      second_stripe_payment_session.StripePaymentSession_checkStripeSessionOpen()
    )

  def test_update_expiration_date(self):
    connector = self._create_connector()
    data = self.data.copy()

    module = self.portal.stripe_payment_session_module
    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        self.session_url,
        json={
          "id": "test_update_expiration_date",
          "status": "open",
          "object": "checkout.session",
          "url": "https://stripe.url"
        },
      )
      rsps.add(
        responses.GET,
        "https://mock:8080/checkout/sessions/test_update_expiration_date",
        json={
          "id": "test_update_expiration_date",
          "status": "open",
          "object": "checkout.session",
        },
      )

      module.StripePaymentSessionModule_createStripeSession(
        connector, data, module.getRelativeUrl())
      self.tic()
      stripe_payment_session = self.portal.portal_catalog.getResultValue(
        portal_type="Stripe Payment Session",
        reference="test_update_expiration_date"
      )
      self.assertEqual("open", stripe_payment_session.getValidationState())
      stripe_payment_session.setExpirationDate(DateTime() - 1)
      self.tic()
      self._document_to_delete_list.append(stripe_payment_session)
      first_expiration_date = stripe_payment_session.getExpirationDate()

      self.portal.portal_alarms.check_stripe_payment_session.activeSense()
      self.tic()
      self.assertGreater(stripe_payment_session.getExpirationDate(), first_expiration_date)

  def test_invalid_request_error(self):
    connector = self._create_connector()
    session_id = "not_found"

    module = self.portal.stripe_payment_session_module
    self.tic()

    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.POST,
        self.session_url,
        self._response_callback(session_id)
      )
      stripe_payment_session = module.StripePaymentSessionModule_createStripeSession(
        connector,
        self.data.copy(),
        module.getRelativeUrl()
      )
      self.tic()
      stripe_payment_session = self.portal.portal_catalog.getResultValue(
        portal_type="Stripe Payment Session",
        reference=session_id
      )
      self._document_to_delete_list.append(stripe_payment_session)

    first_http_exchange, = stripe_payment_session.getFollowUpRelatedValueList(
      portal_type="HTTP Exchange")
    self.assertEqual("acknowledged", first_http_exchange.getValidationState())

    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.GET,
        "https://mock:8080/checkout/sessions/%s" % session_id,
        self._get_response_callback(session_id)
      )
      self.assertRaises(
        requests.HTTPError,
        stripe_payment_session.StripePaymentSession_retrieveSession,
        connector
      )
      self.tic()

  def test_retrieve_stripe_payment_session_status(self):
    connector = self._create_connector()
    session_id = "abc321"

    module = self.portal.stripe_payment_session_module
    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.POST,
        self.session_url,
        self._response_callback(session_id)
      )
      module.StripePaymentSessionModule_createStripeSession(
        connector,
        self.data.copy(),
        module.getRelativeUrl()
      )
      self.tic()
      stripe_payment_session = self.portal.portal_catalog.getResultValue(
        portal_type="Stripe Payment Session",
        reference=session_id)
      http_exchange, = stripe_payment_session.getFollowUpRelatedValueList(portal_type="HTTP Exchange")
      self.assertIn("line_items", json.loads(http_exchange.getRequest()))
      self.assertEqual({
        'status': 'open',
        'url': 'https://stripe.url', 
        'object': 'checkout.session', 
        'id': 'abc321'
        }, json.loads(http_exchange.getResponse()))
      self._document_to_delete_list.append(stripe_payment_session)

    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.GET,
        "https://mock:8080/checkout/sessions/%s" % session_id,
        self._get_response_callback(session_id)
      )
      http_exchange = stripe_payment_session.StripePaymentSession_retrieveSession(
        connector, batch_mode=1
      )
      self.assertEqual("HTTP Exchange", http_exchange.getPortalType())
      self.assertEqual("expired", json.loads(http_exchange.getResponse())["status"])
      self.tic()

  def test_stripe_webhook_endpoint(self):
    connector = self._create_connector()
    session_id = "abc321_webhook"
    module = self.portal.stripe_payment_session_module
    for session in module.searchFolder(reference=session_id):
      module.manage_delObjects(ids=[session.getId(),])
    self.tic()
    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.POST,
        self.session_url,
        self._response_callback(session_id)
      )
      stripe_payment_session = module.StripePaymentSessionModule_createStripeSession(
        connector,
        self.data.copy(),
      )
      self.tic()
      stripe_payment_session = self.portal.portal_catalog.getResultValue(
        portal_type="Stripe Payment Session",
        reference=session_id)
      self._document_to_delete_list.append(stripe_payment_session)
    first_http_exchange, = stripe_payment_session.getFollowUpRelatedValueList(
      portal_type="HTTP Exchange")
    self._document_to_delete_list.append(first_http_exchange)
    self.assertEqual(
      "http_exchange_resource/stripe/create_session",
      first_http_exchange.getResource()
    )
    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.GET,
        "https://mock:8080/checkout/sessions/%s" % session_id,
        self._get_response_callback(session_id)
      )
      ret = self.publish(
        "%s/ERP5Site_receiveStripeWebHook" % self.portal.getPath(),
        stdin=BytesIO(
          json.dumps({
            "id": "evt_%s" % session_id,
            "object": "event",
            "data": {
              "object": {
                "id": session_id,
                "status": "complete",
                "payment_status": "paid",
                "object": "checkout.session"
              }
            }
          }).encode(),
        ),
        request_method="POST",
        env={'CONTENT_TYPE': 'application/json'},
        handle_errors=False)
      self.assertEqual(200, ret.getStatus())
      self.tic()
    second_http_exchange, = [event
      for event in stripe_payment_session.getFollowUpRelatedValueList(portal_type="HTTP Exchange")
      if event != first_http_exchange and event.isMemberOf("resource/http_exchange_resource/stripe/webhook")
    ]
    self.assertEqual("acknowledged", second_http_exchange.getValidationState())
    third_http_exchange, = [event
      for event in stripe_payment_session.getFollowUpRelatedValueList(portal_type="HTTP Exchange")
      if event not in (first_http_exchange, second_http_exchange) and event.isMemberOf("resource/http_exchange_resource/stripe/retrieve_session")
    ]
    self.assertEqual("acknowledged", third_http_exchange.getValidationState())

