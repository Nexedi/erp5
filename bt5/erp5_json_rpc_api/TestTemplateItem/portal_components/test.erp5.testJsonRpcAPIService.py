##############################################################################
# coding: utf-8
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

import io
import json
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from erp5.component.document.OpenAPITypeInformation import byteify


class JsonRpcAPITestCase(ERP5TypeTestCase):
  _type_id = 'JSON RPC Service'
  _action_list_text = ''

  def addJSONForm(self, script_id, input_json_schema=None,
                  after_method_id=None, output_json_schema=None):
    self.portal.portal_callables.newContent(
      portal_type='JSON Form',
      id=script_id,
      text_content=input_json_schema,
      after_method_id=after_method_id,
      response_schema=output_json_schema
    )
    self.tic()
    self._json_form_id_to_cleanup.append(script_id)

  def addPythonScript(self, script_id, params, body):
    skin_folder = self.portal.portal_skins['custom']
    skin_folder.manage_addProduct['ERP5'].addPythonScriptThroughZMI(
      id=script_id)

    self.script = skin_folder.get(script_id)
    self.script.setParameterSignature(params)
    self.script.setBody(body)

    self.tic()
    self._python_script_id_to_cleanup.append(script_id)
    self.portal.changeSkin(None)

  def afterSetUp(self):
    self.connector = self.portal.portal_web_services.newContent(
      portal_type=self._type_id,
      title=self.id(),
      json_form_list=self._action_list_text.split('\n')
    )
    self.tic()
    self._python_script_id_to_cleanup = []
    self._json_form_id_to_cleanup = []

  def beforeTearDown(self):
    self.abort()
    self.tic()
    self.portal.portal_web_services.manage_delObjects([self.connector.getId()])
    self.tic()
    if self._json_form_id_to_cleanup:
      self.portal.portal_callables.manage_delObjects(self._json_form_id_to_cleanup)
    skin_folder = self.portal.portal_skins['custom']
    if self._python_script_id_to_cleanup:
      skin_folder.manage_delObjects(self._python_script_id_to_cleanup)
    self.tic()


  """
  _type_id = NotImplemented  # type: str
  _open_api_schema = NotImplemented  # type: str
  _open_api_schema_content_type = 'application/json'
  _public_api = True

  def afterSetUp(self):
    if self._public_api:
      open_api_type.setTypeWorkflowList(['publication_workflow'])
    self.tic()
    self.connector = self.portal.portal_web_services.newContent(
      portal_type=self._type_id,
      title=self.id(),
    )
    if self._public_api:
      self.connector.publish()
    else:
      self.connector.validate()
    self.tic()
    self._python_script_id_to_cleanup = []

  def beforeTearDown(self):

    skin_folder = self.portal.portal_skins['custom']
    if self._python_script_id_to_cleanup:
      skin_folder.manage_delObjects(self._python_script_id_to_cleanup)
    self.tic()

  def addPythonScript(self, script_id, params, body):
    skin_folder = self.portal.portal_skins['custom']
    skin_folder.manage_addProduct['ERP5'].addPythonScriptThroughZMI(
      id=script_id)
    self._python_script_id_to_cleanup.append(script_id)

    self.script = skin_folder.get(script_id)
    self.script.setParameterSignature(params)
    self.script.setBody(body)

    self.tic()
    self.portal.changeSkin(None)
"""


class TestJsonRpcAPIConnectorView(JsonRpcAPITestCase):
  def test_view(self):
    ret = self.publish(self.connector.getPath(), user='ERP5TypeTestCase')
    self.assertEqual(ret.getStatus(), 200)
    self.assertEqual(ret.getHeader('content-type'), 'text/html; charset=utf-8')
    self.assertIn(b'<html', ret.getBody())

  def test_viewOpenAPIAsJson(self):
    ret = self.publish(
      self.connector.getPath() + '/viewOpenAPIAsJson', user='ERP5TypeTestCase')
    self.assertEqual(ret.getStatus(), 200)
    body = json.load(io.BytesIO(ret.getBody()))
    server_url = body['servers'][0]['url']
    self.assertIn(self.connector.getPath(), server_url)

  def test_erp5_document_methods(self):
    self.connector.setTitle('Pet Store')
    self.assertEqual(self.connector.getTitle(), 'Pet Store')
    self.tic()
    ret = self.publish(
      self.connector.getPath() + '/getTitle', user='ERP5TypeTestCase')
    self.assertEqual(ret.getStatus(), 200)
    self.assertEqual(ret.getBody(), b'Pet Store')

  def test_portal_skins_acquisition(self):
    self.assertEqual(self.connector.JsonRpcService_view.getId(), 'JsonRpcService_view')
    ret = self.publish(
      self.connector.getPath() + '/JsonRpcService_view', user='ERP5TypeTestCase')
    self.assertEqual(ret.getStatus(), 200)
    self.assertNotIn(b'Site Error', ret.getBody())

  def test_non_existing_attribute(self):
    with self.assertRaises(AttributeError):
      _ = self.connector.non_existing_attribute
    ret = self.publish(
      self.connector.getPath() + '/non_existing_attribute',
      user='ERP5TypeTestCase')
    self.assertEqual(ret.getStatus(), 404)
    self.assertEqual(ret.getHeader('content-type'), 'application/json')
    self.assertEqual(
      json.loads(ret.getBody()), {
        "type": "not-found",
        "title": 'non_existing_attribute'
      })


class TestJsonRpcAPIErrorHandling(JsonRpcAPITestCase):
  _action_list_text = '''error.handling.missing.callable | JsonRpcService_doesNotExist
error.handling.callable | JsonRpcService_testExample'''

  def test_requestErrorHandling_wrongContentType(self):
    response = self.publish(
      self.connector.getPath() + '/error.handling.missing.callable',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        json.dumps({}).encode()))
    self.assertEqual(response.getStatus(), 415)
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      json.loads(response.getBody()), {
        "status": 415,
        "type": "unexpected-media-type",
        "title": 'Request Content-Type must be "application/json", not ""'
      })

  def test_requestErrorHandling_wrongHTTPMethod(self):
    response = self.publish(
      self.connector.getPath() + '/error.handling.missing.callable',
      user='ERP5TypeTestCase',
      request_method='GET',
      stdin=io.BytesIO(
        json.dumps({}).encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getStatus(), 405)
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      json.loads(response.getBody()), {
        "status": 405,
        "type": "not-allowed-http-method",
        "title": "Only HTTP POST accepted"
      })

  def test_requestErrorHandling_unknownActionReference(self):
    response = self.publish(
      self.connector.getPath() + '/error.handling.unknown.reference',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        json.dumps({}).encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getStatus(), 404)
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      json.loads(response.getBody()), {
        "type": "not-found",
        "title": "error.handling.unknown.reference"
      })

  def test_requestErrorHandling_unknownCallable(self):
    response = self.publish(
      self.connector.getPath() + '/error.handling.missing.callable',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        json.dumps({}).encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getStatus(), 500)
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      json.loads(response.getBody()), {
        "type": "unknown-error",
        "title": "AttributeError: 'RequestContainer' object has no attribute 'JsonRpcService_doesNotExist'"
      })

  def test_requestErrorHandling_notJsonBody(self):
    self.addJSONForm(
      'JsonRpcService_testExample',
      '{}',
    )
    response = self.publish(
      self.connector.getPath() + '/error.handling.callable',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        '1+2:"'.encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getStatus(), 400)
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      json.loads(response.getBody()), {
        "status": 400,
        "type": "not-parsable-json-content",
        "title": "Extra data: line 1 column 2 - line 1 column 6 (char 1 - 5)"
      })

  def test_requestErrorHandling_notJsonDict(self):
    self.addJSONForm(
      'JsonRpcService_testExample',
      '{}',
    )
    response = self.publish(
      self.connector.getPath() + '/error.handling.callable',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        '[]'.encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getStatus(), 400)
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      json.loads(response.getBody()), {
        "status": 400,
        "type": "not-json-object-content",
        "title": "Did not received a JSON Object"
      })

  def test_requestErrorHandling_badWebServiceConfiguration(self):
    self.connector.edit(json_form_list=('foobarmissingseparator',))
    response = self.publish(
      self.connector.getPath() + '/error.handling.callable',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        '{}'.encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getStatus(), 500)
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      json.loads(response.getBody()), {
        "type": "unknown-error",
        "title": "ValueError: Unparsable configuration: foobarmissingseparator"
      })

  def test_requestErrorHandling_notJsonForm(self):
    self.connector.edit(json_form_list=('not.a.json.form | JsonRpcService_view',))
    response = self.publish(
      self.connector.getPath() + '/not.a.json.form',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        '{}'.encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getStatus(), 500)
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      json.loads(response.getBody()), {
        "type": "unknown-error",
        "title": "ValueError: JsonRpcService_view is not a JSON Form"
      })

  def test_requestErrorHandling_invalidInputJsonSchema(self):
    self.addJSONForm(
      'JsonRpcService_testExample',
      '1/2',
    )
    response = self.publish(
      self.connector.getPath() + '/error.handling.callable',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        '{}'.encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getStatus(), 500)
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      json.loads(response.getBody()), {
        'title': 'ValueError: Extra data: line 1 column 2 - line 1 column 4 (char 1 - 3)',
        'type': 'unknown-error'
      })

  def test_requestErrorHandling_unknownAfterMethod(self):
    self.addJSONForm(
      'JsonRpcService_testExample',
      '{}',
      after_method_id='THISSCRIPTDOESNOTEXIST',
    )
    response = self.publish(
      self.connector.getPath() + '/error.handling.callable',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        '{}'.encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getStatus(), 500)
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      json.loads(response.getBody()), {
        "type": "unknown-error",
        "title": "AttributeError: 'RequestContainer' object has no attribute 'THISSCRIPTDOESNOTEXIST'"
      })

  def test_requestErrorHandling_failingAfterMethod(self):
    self.addPythonScript(
      'JsonRpcService_fail',
      'data_dict, json_form',
      '1//0',
    )
    self.addJSONForm(
      'JsonRpcService_testExample',
      '{}',
      after_method_id='JsonRpcService_fail',
    )
    response = self.publish(
      self.connector.getPath() + '/error.handling.callable',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        '{}'.encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getStatus(), 500)
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      json.loads(response.getBody()), {
        "type": "unknown-error",
        "title": "ZeroDivisionError: integer division or modulo by zero"
      })

  def test_requestErrorHandling_abortTransactionOnError(self):
    self.addPythonScript(
      'JsonRpcService_fail',
      'data_dict, json_form',
      'context.getPortalObject().setTitle("ooops")\n'
      '1/0',
    )
    self.addJSONForm(
      'JsonRpcService_testExample',
      '{}',
      after_method_id='JsonRpcService_fail',
    )
    response = self.publish(
      self.connector.getPath() + '/error.handling.callable',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        '{}'.encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getStatus(), 500)
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      json.loads(response.getBody()), {
        "type": "unknown-error",
        "title": "ZeroDivisionError: integer division or modulo by zero"
      })
    self.assertNotEqual(self.portal.getTitle(), "ooops")

  def test_requestErrorHandling_noOutputWithOutputSchema(self):
    self.addPythonScript(
      'JsonRpcService_returnNothing',
      'data_dict, json_form',
      'context.getPortalObject().setTitle("ooops")\n'
    )
    self.addJSONForm(
      'JsonRpcService_testExample',
      '{}',
      output_json_schema='''{"$schema": "https://json-schema.org/draft/2020-12/schema",
      "type": "object",
      "properties": {"foo": {"type": "string"}}}''',
      after_method_id='JsonRpcService_returnNothing',
    )
    response = self.publish(
      self.connector.getPath() + '/error.handling.callable',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        '{}'.encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getStatus(), 500)
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      json.loads(response.getBody()), {
        "type": "unknown-error",
        "title": "ValueError: JsonRpcService_testExample has an output schema but response is empty"
      })
    self.assertNotEqual(self.portal.getTitle(), "ooops")

  def test_requestErrorHandling_emptyOutputWithOutputSchema(self):
    self.addPythonScript(
      'JsonRpcService_returnNothing',
      'data_dict, json_form',
      'context.getPortalObject().setTitle("ooops")\n'
      'return {}'
    )
    self.addJSONForm(
      'JsonRpcService_testExample',
      '{}',
      output_json_schema='''{"$schema": "https://json-schema.org/draft/2020-12/schema",
      "type": "object",
      "properties": {"foo": {"type": "string"}}}''',
      after_method_id='JsonRpcService_returnNothing',
    )
    response = self.publish(
      self.connector.getPath() + '/error.handling.callable',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        '{}'.encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getStatus(), 500)
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      json.loads(response.getBody()), {
        "type": "unknown-error",
        "title": "ValueError: JsonRpcService_testExample has an output schema but response is empty"
      })
    self.assertNotEqual(self.portal.getTitle(), "ooops")

  def test_requestErrorHandling_invalidOutputWithOutputSchema(self):
    self.addPythonScript(
      'JsonRpcService_returnNothing',
      'data_dict, json_form',
      'context.getPortalObject().setTitle("ooops")\n'
      'return {"foo": 2}'
    )
    self.addJSONForm(
      'JsonRpcService_testExample',
      '{}',
      output_json_schema='''{"$schema": "https://json-schema.org/draft/2020-12/schema",
      "type": "object",
      "properties": {"foo": {"type": "string"}}}''',
      after_method_id='JsonRpcService_returnNothing',
    )
    response = self.publish(
      self.connector.getPath() + '/error.handling.callable',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        '{}'.encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getStatus(), 500)
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      json.loads(response.getBody()), {
        "type": "unknown-error",
        "title": "ValueError: 2 is not of type u'string'"
      })
    self.assertNotEqual(self.portal.getTitle(), "ooops")

  def test_requestErrorHandling_outputWithoutOutputSchema(self):
    self.addPythonScript(
      'JsonRpcService_returnNothing',
      'data_dict, json_form',
      'context.getPortalObject().setTitle("ooops")\n'
      'return {"foo": 2}'
    )
    self.addJSONForm(
      'JsonRpcService_testExample',
      '{}',
      after_method_id='JsonRpcService_returnNothing',
    )
    response = self.publish(
      self.connector.getPath() + '/error.handling.callable',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        '{}'.encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getStatus(), 500)
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      json.loads(response.getBody()), {
        "type": "unknown-error",
        "title": "ValueError: JsonRpcService_testExample does not have an output schema but response is not empty"
      })
    self.assertNotEqual(self.portal.getTitle(), "ooops")


class TestJsonRpcAPIJsonFormHandling(JsonRpcAPITestCase):
  _action_list_text = '''json.form.handling.callable | JsonRpcService_callFromTest'''

  def test_jsonFormHandling_emptyUseCase(self):
    # No input json schema
    # No output json schema
    # No BODY
    self.addJSONForm(
      'JsonRpcService_callFromTest',
      '{}',
    )
    response = self.publish(
      self.connector.getPath() + '/json.form.handling.callable',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        '{}'.encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getStatus(), 200)
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      byteify(json.loads(response.getBody())),
      {
        'type': 'success-type',
        'title': "query completed",
        'status': 200
      })

  def test_jsonFormHandling_noInputSchemaAndBodyContent(self):
    self.addJSONForm(
      'JsonRpcService_callFromTest',
      '{}',
    )
    response = self.publish(
      self.connector.getPath() + '/json.form.handling.callable',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        '{"a": "b"}'.encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getStatus(), 200)
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      byteify(json.loads(response.getBody())),
      {
        'type': 'success-type',
        'title': "query completed",
        'status': 200
      })

  def test_jsonFormHandling_invalidBodyContent(self):
    self.addJSONForm(
      'JsonRpcService_callFromTest',
      '''{"$schema": "https://json-schema.org/draft/2020-12/schema",
      "type": "object",
      "properties": {"foo": {"type": "string"}}}'''
    )
    response = self.publish(
      self.connector.getPath() + '/json.form.handling.callable',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        '{"foo": 1}'.encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(
      response.getBody(),
      json.dumps(
        {
          'title': "1 is not of type u'string'",
          'type': "invalid-json-object-content",
          'status': 400
        }).encode())
    self.assertEqual(response.getStatus(), 400)

  def test_jsonFormHandling_customError(self):
    self.addPythonScript(
      'JsonRpcService_customError',
      'data_dict, json_form',
      'context.getPortalObject().setTitle("ooops")\n'
      'from erp5.component.document.JsonRpcAPIService import JsonRpcAPIError\n'
      'class CustomError(JsonRpcAPIError):\n'
      '  type = "custom-error-type"\n'
      '  status = 417\n'
      'raise CustomError("custom error title")',
    )
    self.addJSONForm(
      'JsonRpcService_callFromTest',
      '{}',
      after_method_id='JsonRpcService_customError',
    )
    response = self.publish(
      self.connector.getPath() + '/json.form.handling.callable',
      user='ERP5TypeTestCase',
      request_method='POST',
      stdin=io.BytesIO(
        '{}'.encode()),
      env={'CONTENT_TYPE': 'application/json'}
    )
    self.assertNotEqual(self.portal.getTitle(), "ooops")
    self.assertEqual(
      response.getBody(),
      json.dumps(
        {
          'type': 'custom-error-type',
          'title': "custom error title",
          'status': 417
        }).encode())
    self.assertEqual(response.getHeader('content-type'), 'application/json')
    self.assertEqual(response.getStatus(), 417)
