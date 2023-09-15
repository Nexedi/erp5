##############################################################################
#
# Copyright (c) 2002-2023 Nexedi SA and Contributors. All Rights Reserved.
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

import string
import random
import urllib
import msgpack

from httplib import NO_CONTENT
from cStringIO import StringIO
from App.version_txt import getZopeVersion
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


if getZopeVersion() < (4, ):
  NO_CONTENT = 200


def getRandomString():
  return "test.%s" %"".join([random.choice(string.ascii_letters + string.digits) for _ in xrange(32)])


class TestDataIngestion(ERP5TypeTestCase):
  """
  Test Class for Data Ingestion via MQTT
  """

  def getTitle(self):
    return "Wendelin Data Ingestion Test for MQTT"


  def _sendIngestionRequest(self, topic, payload, ingestion_policy, data_supply, data_product):
    """
    Send an ingestion request with the given topic and payload.
    """

    data_chunk = {
      "topic": topic,
      "payload": payload
    }

    body = msgpack.packb([0, data_chunk], use_bin_type=True)
    env = { "CONTENT_TYPE": "application/x-www-form-urlencoded" }
    body = urllib.urlencode({ "data_chunk": body })

    if not isinstance(ingestion_policy, str):
      ingestion_policy = ingestion_policy.getPath()

    if not isinstance(data_supply, str):
      data_supply = data_supply.getReference()

    if not isinstance(data_product, str):
      data_product = data_product.getReference()

    path = ingestion_policy + "/ingest?reference=" + data_supply + "." + data_product
    publish_kw = dict(user="ERP5TypeTestCase", env=env, request_method="POST", stdin=StringIO(body))
    response = self.publish(path, **publish_kw)

    return response


  def _assertIngestion(self, topic, payload):
    """
    Send an ingestion request and assert the response and the resulting MQTT message.
    """

    # Get ingestion policy, data supply, and data product
    ingestion_policy = self.portal.portal_ingestion_policies.default_mqtt
    data_supply = self.portal.data_supply_module.default_mqtt
    data_product = self.portal.data_product_module.default_mqtt

    response = self._sendIngestionRequest(topic, payload, ingestion_policy, data_supply, data_product)

    # Assert the response status codes
    self.assertEqual(NO_CONTENT, response.getStatus())
    self.tic()

    # Get the latest MQTT Message
    mqtt_message = self.portal.portal_catalog.getResultValue(portal_type="MQTT Message", title=topic)

    # Assert the topic and the payload
    self.assertEqual(mqtt_message.getTitle(), topic)
    self.assertEqual(mqtt_message.getPayload(), str(payload))


  def test_IngestionFromMQTT(self):
    """
    Test ingestion using a POST Request containing a
    msgpack encoded message simulating input from MQTT.
    """

    topic = getRandomString()
    message = getRandomString()

    payload = {
      "message": message
    }

    self._assertIngestion(topic, payload)


  def test_IngestionFromMQTTWithMultipleMessages(self):
    """
    Test ingestion using a POST Request containing a
    msgpack encoded messages simulating input from MQTT.
    """

    topic = getRandomString()
    message1 = getRandomString()
    message2 = getRandomString()

    payload = {
      "message1": message1,
      "message2": message2
    }

    self._assertIngestion(topic, payload)


  def test_IngestionWithInvalidPolicy(self):
    """
    Test ingestion using an invalid ingestion policy.
    """

    topic = getRandomString()
    message1 = getRandomString()
    message2 = getRandomString()

    invalid_policy = "invalid_policy_name"
    data_supply = self.portal.data_supply_module.default_mqtt
    data_product = self.portal.data_product_module.default_mqtt

    payload = {
      "message1": message1,
      "message2": message2
    }

    response = self._sendIngestionRequest(topic, payload, invalid_policy, data_supply, data_product)

    self.assertEqual(404, response.getStatus())
    self.tic()


  def test_IngestionWithInvalidDataSupply(self):
    """
    Test ingestion using an invalid data supply.
    """

    topic = getRandomString()
    message1 = getRandomString()
    message2 = getRandomString()

    invalid_policy = self.portal.portal_ingestion_policies.default_mqtt
    data_supply = "invalid_supply_name"
    data_product = self.portal.data_product_module.default_mqtt

    payload = {
      "message1": message1,
      "message2": message2
    }

    response = self._sendIngestionRequest(topic, payload, invalid_policy, data_supply, data_product)

    self.assertEqual(500, response.getStatus())
    self.tic()


  def test_IngestionWithInvalidDataProduct(self):
    """
    Test ingestion using an invalid data product.
    """

    topic = getRandomString()
    message1 = getRandomString()
    message2 = getRandomString()

    invalid_policy = self.portal.portal_ingestion_policies.default_mqtt
    data_supply = self.portal.data_supply_module.default_mqtt
    data_product = "invalid_product_name"

    payload = {
      "message1": message1,
      "message2": message2
    }

    response = self._sendIngestionRequest(topic, payload, invalid_policy, data_supply, data_product)

    self.assertEqual(500, response.getStatus())
    self.tic()

  def test_MultipleIngestions(self):
    """
    Test multiple data ingestion requests in succession.
    """

    topic1 = getRandomString()
    message1 = getRandomString()

    topic2 = getRandomString()
    message2 = getRandomString()

    payload1 = {
      "message1": message1
    }

    payload2 = {
      "message2": message2
    }

    self._assertIngestion(topic1, payload1)
    self._assertIngestion(topic2, payload2)