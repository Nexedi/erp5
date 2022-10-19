# -*- coding: utf-8 -*-
# Copyright (c) 2002-2015 Nexedi SA and Contributors. All Rights Reserved.
from json import dumps
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from six.moves.http_client import HTTPSConnection
from erp5.component.mixin.RESTAPIClientConnectorMixin import RESTAPIClientConnectorMixin
from ssl import SSLError
from Products.ERP5Type.Timeout import TimeoutReachedError
import mock

expected_output_body_dict = {
  u'output': 'output',
}
input_body_dict = {
  'input': 'input',
}

class HTTPResponse_getresponse():
  def __init__(self, status=200):
    self.status = status

  def getheaders(self):
    return [
      ('content-type', 'application/json'),
    ]

  def read(self):
    return dumps(expected_output_body_dict)

class RESTAPIError(Exception):
  __allow_access_to_unprotected_subobjects__ = {
    'header_dict': 1,
    'body': 1,
    'status': 1,
  }

  def __init__(self, header_dict, body, status):
    super(RESTAPIError, self).__init__()
    self.header_dict = header_dict
    self.body = body
    self.status = status

class RESTAPIClientConnector(RESTAPIClientConnectorMixin):
  meta_type = 'REST API Client Connector'
  security = RESTAPIClientConnectorMixin.security
  ClientConnectorError = RESTAPIError

  def _getAccessToken(self):
    return 'access_token'
  
  def getTimeout(self, timeout):
    return 5

  def getBaseUrl(self):
    return 'https://example.com/'
  
  def getCaCertificatePem(self):
    return 'ca_certificate_pem'

  def getBindAddress(self):
    return 'bind_address'

class TestRESTAPIClientConnector(ERP5TypeTestCase):

  def afterSetUp(self):
    self.rest_api_client_connection = RESTAPIClientConnector(id='rest_api_client_connection')

  def test_api_call(self):
    timeout = 1

    with mock.patch(
      'ssl.create_default_context',
    ) as mock_ssl_create_default_context, mock.patch(
      'six.moves.http_client.HTTPSConnection.request',
    ) as mock_https_connection_request, mock.patch(
      'six.moves.http_client.HTTPSConnection.getresponse',
      return_value=HTTPResponse_getresponse()
    ), mock.patch('six.moves.http_client.HTTPSConnection', return_value=HTTPSConnection) as mock_https_connection:
      header_dict, body_dict, status = self.rest_api_client_connection.call(
        archive_resource=None,
        method='POST',
        path='/path',
        body=input_body_dict,
        timeout=timeout,
      )

      # Check request
      ssl_create_default_context_argument_dict = mock_ssl_create_default_context.call_args.kwargs
      self.assertEqual(
        ssl_create_default_context_argument_dict['cadata'],
        'ca_certificate_pem'
      )

      https_connection_argument_dict = mock_https_connection.call_args.kwargs
      self.assertTrue(
        https_connection_argument_dict['timeout'] <= timeout
      )
      self.assertEqual(
        https_connection_argument_dict['host'],
        'example.com'
      )
      self.assertEqual(
        https_connection_argument_dict['source_address'],
        ('bind_address', 0)
      )

      https_connection_request_argument_dict = mock_https_connection_request.call_args.kwargs
      self.assertEqual(
        https_connection_request_argument_dict['body'],
        dumps(input_body_dict)
      )
      self.assertEqual(
        https_connection_request_argument_dict['url'],
        '/path'
      )
      self.assertEqual(
        https_connection_request_argument_dict['headers']['Authorization'],
        'Bearer access_token'
      )
      self.assertEqual(
        https_connection_request_argument_dict['headers']['content-type'],
        'application/json'
      )
      self.assertEqual(
        https_connection_request_argument_dict['method'],
        'POST'
      )

      # Check response
      self.assertEqual(
        header_dict['content-type'],
        'application/json'
      )
      self.assertEqual(
        body_dict,
        expected_output_body_dict
      )
      self.assertEqual(
        status,
        200
      )


  def test_api_call_error(self):
    with mock.patch(
      'ssl.create_default_context',
    ), mock.patch(
      'six.moves.http_client.HTTPSConnection.request',
    ), mock.patch(
      'six.moves.http_client.HTTPSConnection.getresponse',
      return_value=HTTPResponse_getresponse(498)
    ):
      with self.assertRaises(RESTAPIError) as error:
        self.rest_api_client_connection.call(
          archive_resource=None,
          method='POST',
          path='/path',
          body=input_body_dict
        )
        
        self.assertEqual(
          error.status,
          498
        )
        self.assertEqual(
          error.header_dict['content-type'],
          'application/json'
        )
        self.assertEqual(
          error.body,
          expected_output_body_dict
        )

  def test_api_call_timeout(self):
    with mock.patch(
      'ssl.create_default_context',
    ), mock.patch(
      'six.moves.http_client.HTTPSConnection.request',
    ), mock.patch(
      'six.moves.http_client.HTTPSConnection.getresponse',
    ) as mock_https_connection_getresponse:
      mock_https_connection_getresponse.side_effect = SSLError('The read operation timed out')
      self.assertRaises(
        TimeoutReachedError,
        self.rest_api_client_connection.call,
        archive_resource=None,
        method='POST',
        path='/path',
        body=input_body_dict
      )