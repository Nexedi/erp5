# -*- coding: utf-8 -*-
# Copyright (c) 2002-2015 Nexedi SA and Contributors. All Rights Reserved.
from json import dumps
from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import mock

expected_body_dict = {
  u'input_tokens': 18,
  u'translations': [{
    u'text': u'Le renard brun rapide saute sur le chien paresseux.',
    u'detected_source_lang': u'en',
  }],
  u'output_tokens': 85
}

class HTTPResponse_translate():
  def __init__(self, status=200):
    self.status = status

  def getheaders(self):
    return [
      ('date', DateTime().strftime('%a, %d %b %Y %H:%M:%S GMT')),
      ('transfer-encoding', 'chunked'),
      ('server', 'Apache'),
      ('content-type', 'application/json'),
      ('x-accel-buffering', 'no'),
    ]

  def read(self):
    return dumps(expected_body_dict)

class TestTextSynthClientConnector(ERP5TypeTestCase):

  def afterSetUp(self):
    portal = self.portal
    portal_web_services = portal.portal_web_services
    textsynth_web_service_id = 'textsynth'
    if textsynth_web_service_id in portal_web_services:
      portal_web_services.manage_delObjects([textsynth_web_service_id])
    text_synth_connection = portal_web_services.newContent(
      id=textsynth_web_service_id,
      portal_type='TextSynth Client Connector',
      reference=textsynth_web_service_id,
      base_url='http://www.textsynth.rapid.space/',
      client_secret='APIKEY',
      timeout=1,
    )
    text_synth_connection.validate()
    self.text_synth_connection = text_synth_connection

  def test_translate(self):
    with mock.patch(
      'httplib.HTTPSConnection.request',
    ), mock.patch(
      'httplib.HTTPSConnection.getresponse',
      return_value=HTTPResponse_translate()
    ):
      header_dict, body_dict, status = self.text_synth_connection.translate(
        text='The quick brown fox jumps over the lazy dog.',
        target_lang='fr',
        source_lang='en',
      )
      self.assertEqual(
        header_dict['content-type'],
        'application/json'
      )
      self.assertEqual(
        body_dict,
        expected_body_dict
      )
      self.assertEqual(
        status,
        200
      )
