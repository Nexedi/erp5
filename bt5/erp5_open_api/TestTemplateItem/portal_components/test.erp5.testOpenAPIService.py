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

import six
# pylint:disable=no-name-in-module
if six.PY2:
  from base64 import encodestring as base64_encodebytes
else:
  from base64 import encodebytes as base64_encodebytes
# pylint:enable=no-name-in-module
import io
import json
import unittest

try:
  import yaml
except ImportError:
  yaml = None

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class OpenAPITestCase(ERP5TypeTestCase):
  _type_id = NotImplemented  # type: str
  _open_api_schema = NotImplemented  # type: str
  _open_api_schema_content_type = 'application/json'
  _public_api = True

  def afterSetUp(self):
    open_api_type = self.portal.portal_types.newContent(
      portal_type='Open API Type',
      id=self._type_id,
      text_content=self._open_api_schema,
    )
    open_api_type.setContentType(self._open_api_schema_content_type, )
    if self._public_api:
      open_api_type.setTypeWorkflowList(['publication_workflow'])
    web_service_tool_type = self.portal.portal_types['Web Service Tool']
    web_service_tool_type.setTypeAllowedContentTypeList(
      sorted(
        set(web_service_tool_type.getTypeAllowedContentTypeList())
        | set([self._type_id])))
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
    self.abort()
    self.tic()
    if self.portal.portal_types.get(self._type_id):
      self.portal.portal_types.manage_delObjects([self._type_id])
      web_service_tool_type = self.portal.portal_types['Web Service Tool']
      web_service_tool_type.setTypeAllowedContentTypeList(
        sorted(
          set(web_service_tool_type.getTypeAllowedContentTypeList())
          - set([self._type_id])))
      connector_id_list = [
        c.getId() for c in self.portal.portal_web_services.contentValues(
          portal_type=self._type_id)
      ]
      if connector_id_list:
        self.portal.portal_web_services.manage_delObjects(connector_id_list)

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


class OpenAPIPetStoreTestCase(OpenAPITestCase):
  _type_id = 'Test Pet Store Open API'

  @property
  def _open_api_schema(self):
    return bytes(
      self.portal.portal_skins.erp5_open_api['test-petstore-swagger.json'])


class TestOpenAPIConnectorView(OpenAPIPetStoreTestCase):
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
    self.assertEqual(self.connector.OpenAPIService_view.getId(), 'OpenAPIService_view')
    ret = self.publish(
      self.connector.getPath() + '/OpenAPIService_view', user='ERP5TypeTestCase')
    self.assertEqual(ret.getStatus(), 200)
    self.assertNotIn(b'Error', ret.getBody())

  def test_non_existing_attribute(self):
    with self.assertRaises(AttributeError):
      _ = self.connector.non_existing_attribute
    ret = self.publish(
      self.connector.getPath() + '/non_existing_attribute',
      user='ERP5TypeTestCase')
    self.assertEqual(ret.getStatus(), 404)


class TestOpenScriptGeneration(OpenAPIPetStoreTestCase):
  def test_generate_scripts(self):
    self.portal.portal_skins.manage_addProduct['OFSP'].manage_addFolder(
      self.id())
    skin_folder = self.portal.portal_skins[self.id()]
    self.portal.portal_types[
      'Test Pet Store Open API'].OpenAPIType_generatePythonScriptForOperations(
        self.id())
    self.assertEqual(
      sorted(skin_folder.objectIds()), [
        'TestPetStoreOpenAPI_addPet',
        'TestPetStoreOpenAPI_createUser',
        'TestPetStoreOpenAPI_createUsersWithListInput',
        'TestPetStoreOpenAPI_deleteOrder',
        'TestPetStoreOpenAPI_deletePet',
        'TestPetStoreOpenAPI_deleteUser',
        'TestPetStoreOpenAPI_findPetsByStatus',
        'TestPetStoreOpenAPI_findPetsByTags',
        'TestPetStoreOpenAPI_getInventory',
        'TestPetStoreOpenAPI_getOrderById',
        'TestPetStoreOpenAPI_getPetById',
        'TestPetStoreOpenAPI_getUserByName',
        'TestPetStoreOpenAPI_loginUser',
        'TestPetStoreOpenAPI_logoutUser',
        'TestPetStoreOpenAPI_placeOrder',
        'TestPetStoreOpenAPI_updatePet',
        'TestPetStoreOpenAPI_updatePetWithForm',
        'TestPetStoreOpenAPI_updateUser',
        'TestPetStoreOpenAPI_uploadFile',
      ])
    self.assertEqual(
      skin_folder.TestPetStoreOpenAPI_deletePet.getParameterSignature(),
      'api_key, petId')
    self.assertEqual(
      skin_folder.TestPetStoreOpenAPI_createUser.getParameterSignature(),
      'body')
    self.assertEqual(
      skin_folder.TestPetStoreOpenAPI_updateUser.getParameterSignature(),
      'username, body')
    self.assertEqual(
      skin_folder.TestPetStoreOpenAPI_getInventory.getParameterSignature(), '')

    self.assertEqual(
      skin_folder.TestPetStoreOpenAPI_getInventory.getBody(),
      '''"""Returns a map of status codes to quantities

GET /store/inventory
"""
''')


class TestOpenAPIServicePetController(OpenAPIPetStoreTestCase):
  def test_add_pet(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_addPet',
      'body',
      'return "ok" if (body["id"] == 10 and body["name"] == "doggie") else repr(body)',
    )
    response = self.publish(
      self.connector.getPath() + '/pet',
      request_method='POST',
      stdin=io.BytesIO(
        json.dumps(
          {
            "category": {
              "id": 1,
              "name": "Dogs"
            },
            "status": "available",
            "name": "doggie",
            "tags": [{
              "id": 0,
              "name": "string"
            }],
            "photoUrls": ["string"],
            "id": 10
          }).encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getBody(), b'"ok"')
    self.assertEqual(response.getStatus(), 200)

  def test_delete_pet(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_deletePet',
      '**kw',
      'return "ok" if kw == {"api_key": "key", "petId": 789} else repr(kw)',
    )
    response = self.publish(
      self.connector.getPath() + '/pet/789',
      request_method='DELETE',
      env={'HTTP_API_KEY': "key"},
    )
    self.assertEqual(response.getBody(), b'"ok"')
    self.assertEqual(response.getStatus(), 200)

  def test_find_pets_by_status(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_findPetsByStatus',
      'status',
      'return "ok" if status == "available" else repr(status)',
    )
    response = self.publish(
      self.connector.getPath() + '/pet/findByStatus?status=available')
    self.assertEqual(response.getBody(), b'"ok"')
    self.assertEqual(response.getStatus(), 200)

  def test_find_pets_by_tags(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_findPetsByTags',
      'tags',
      'return tags',
    )
    response = self.publish(
      self.connector.getPath() + '/pet/findByTags?tags=a&tags=b')
    self.assertEqual(response.getStatus(), 200)
    self.assertEqual(response.getBody(), json.dumps(['a', 'b']).encode())

    response = self.publish(
      self.connector.getPath() + '/pet/findByTags?tags=tag_example')
    self.assertEqual(response.getStatus(), 200)
    self.assertEqual(response.getBody(), json.dumps(['tag_example']).encode())

  def test_get_pet_by_id(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_getPetById',
      'petId',
      'return "ok" if petId == 789 else repr(petId)',
    )
    response = self.publish(self.connector.getPath() + '/pet/789')
    self.assertEqual(response.getBody(), b'"ok"')
    self.assertEqual(response.getStatus(), 200)

  def test_get_pet_by_id_traverse_subpath(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_getPetById',
      'petId',
      'return "ok" if traverse_subpath == ["pet", "789"] else repr(traverse_subpath)',
    )
    response = self.publish(self.connector.getPath() + '/pet/789')
    self.assertEqual(response.getBody(), b'"ok"')
    self.assertEqual(response.getStatus(), 200)

  def test_update_pet(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_updatePet',
      'body',
      'return "ok" if ('
      ' body["category"]["id"] == 1'
      ' and body["category"]["name"] == "Dogs"'
      ' and body["status"] == "available"'
      ' and body["tags"] == [{"id": 0, "name": "string"}]'
      ' and body["photoUrls"] == ["string"]'
      ' and body["id"] == 10'
      ' ) else repr(body)',
    )
    response = self.publish(
      self.connector.getPath() + '/pet',
      request_method='PUT',
      stdin=io.BytesIO(
        json.dumps(
          {
            "category": {
              "id": 1,
              "name": "Dogs"
            },
            "status": "available",
            "name": "doggie",
            "tags": [{
              "id": 0,
              "name": "string"
            }],
            "photoUrls": ["string"],
            "id": 10
          }).encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getBody(), b'"ok"')
    self.assertEqual(response.getStatus(), 200)

  def test_update_pet_with_form(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_updatePetWithForm',
      'petId, name, status',
      'return "ok" if ('
      'petId == 789'
      ' and name == "name"'
      ' and status == "status"'
      ') else repr((petId, name, status))',
    )
    response = self.publish(
      self.connector.getPath() + '/pet/789?name=name&status=status',
      request_method='POST',
      env={'CONTENT_TYPE': 'application/x-www-form-urlencoded'})
    self.assertEqual(response.getBody(), b'"ok"')
    self.assertEqual(response.getStatus(), 200)

  def test_upload_file(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_uploadFile',
      'petId, body, additionalMetadata',
      'return "ok" if ('
      'petId == 789'
      ' and body == b"file content"'
      ' and additionalMetadata == "additional"'
      ') else repr((petId, body, additionalMetadata))',
    )
    response = self.publish(
      self.connector.getPath()
      + '/pet/{petId}/uploadImage?additionalMetadata=additional'.format(
        petId=789),
      request_method='POST',
      stdin=io.BytesIO(b'file content'),
      env={"CONTENT_TYPE": 'application/octet-stream'})

    self.assertEqual(response.getBody(), b'"ok"')
    self.assertEqual(response.getStatus(), 200)


@unittest.skipIf(yaml is None, 'PyYAML is required for yaml tests')
class TestOpenAPIServiceYaml(OpenAPITestCase):
  _type_id = 'Test Open API YAML'
  _open_api_schema_content_type = 'application/x-yaml'
  _open_api_schema = '''
openapi: 3.0.3
info:
  title: TestOpenAPIServiceYaml
  version: 0.0.0
paths:
  '/users/{user_id}':
    get:
      operationId: testGET
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
'''

  def test_get(self):
    self.addPythonScript(
      'TestOpenAPIYAML_testGET',
      'user_id',
      'return "ok" if user_id == 123 else repr(user_id)',
    )
    response = self.publish(self.connector.getPath() + '/users/123')
    self.assertEqual(response.getBody(), b'"ok"')
    self.assertEqual(response.getStatus(), 200)


class TestPathParameterSerialization(OpenAPITestCase):
  _type_id = 'Test Open API Parameter Serialization'

  @property
  def _open_api_schema(self):
    primitive_params = []
    array_params = []
    for style in ('simple', 'label', 'matrix'):
      for explode in (True, False):
        primitive_params.append(
          {
            'name': '{style}_{explode}'.format(style=style, explode=explode),
            'in': 'path',
            'schema': {
              'type': 'integer'
            },
            'style': style,
            'explode': explode
          })
        array_params.append(
          {
            'name': '{style}_{explode}'.format(style=style, explode=explode),
            'in': 'path',
            'schema': {
              'type': 'array',
              'items': {
                'type': 'integer'
              }
            },
            'style': style,
            'explode': explode
          })

    return json.dumps(
      {
        'paths': {
          '/primitive/{simple_False}/{simple_True}'
          '/{label_False}/{label_True}'
          '/{matrix_False}/{matrix_True}': {
            'get': {
              'operationId': 'testPrimitiveSerialization',
              'parameters': primitive_params
            }
          },
          '/array/{simple_False}/{simple_True}'
          '/{label_False}/{label_True}'
          '/{matrix_False}/{matrix_True}': {
            'get': {
              'operationId': 'testArraySerialization',
              'parameters': array_params
            }
          }
        }
      })

  def test_primitive_parameter_serialization(self):
    self.addPythonScript(
      'TestOpenAPIParameterSerialization_testPrimitiveSerialization',
      'simple_False, simple_True, label_False, label_True, matrix_False, matrix_True',
      'return "ok" if ('
      'simple_False == 5'
      ' and simple_True == 5'
      ' and label_False == 5'
      ' and label_True == 5'
      ' and matrix_False == 5'
      ' and matrix_True == 5'
      ') else repr((simple_False, simple_True, label_False, label_True, matrix_False, matrix_True))',
    )

    response = self.publish(
      self.connector.getPath() + '/primitive/5/5/.5/.5'
      + '/;matrix_False=5/;matrix_True=5')
    self.assertEqual(response.getBody(), b'"ok"')
    self.assertEqual(response.getStatus(), 200)

  def test_array_parameter_serialization(self):
    self.addPythonScript(
      'TestOpenAPIParameterSerialization_testArraySerialization',
      'simple_False, simple_True, label_False, label_True, matrix_False, matrix_True',
      'return "ok" if ('
      'simple_False == [3,4,5]'
      ' and simple_True == [3,4,5]'
      ' and label_False == [3,4,5]'
      ' and label_True == [3,4,5]'
      ' and matrix_False == [3,4,5]'
      ' and matrix_True == [3,4,5]'
      ') else repr((simple_False, simple_True, label_False, label_True, matrix_False, matrix_True))',
    )

    response = self.publish(
      self.connector.getPath() + '/array/3,4,5/3,4,5/.3,4,5/.3.4.5'
      + '/;matrix_False=3,4,5/;matrix_True=3;matrix_True=4;matrix_True=5',
      handle_errors=False)
    self.assertEqual(response.getBody(), b'"ok"')
    self.assertEqual(response.getStatus(), 200)


class TestQueryParameterSerialization(OpenAPITestCase):
  _type_id = 'Test Open API Parameter Serialization'

  @property
  def _open_api_schema(self):
    array_params = []
    for style in ('form', 'spaceDelimited', 'pipeDelimited'):
      for explode in (True, False):
        array_params.append(
          {
            'name': '{style}_{explode}'.format(style=style, explode=explode),
            'in': 'query',
            'schema': {
              'type': 'array',
              'items': {
                'type': 'integer'
              }
            },
            'style': style,
            'explode': explode
          })

    return json.dumps(
      {
        'paths': {
          '/array': {
            'get': {
              'operationId': 'testArraySerialization',
              'parameters': array_params
            }
          }
        }
      })

  def test_array_parameter_serialization(self):
    self.addPythonScript(
      'TestOpenAPIParameterSerialization_testArraySerialization',
      'form_False, form_True, spaceDelimited_False, spaceDelimited_True, '
      'pipeDelimited_False, pipeDelimited_True',
      'return "ok" if ('
      'form_False == [3,4,5]'
      ' and form_True == [3,4,5]'
      ' and spaceDelimited_False == [3,4,5]'
      ' and spaceDelimited_True == [3,4,5]'
      ' and pipeDelimited_False == [3,4,5]'
      ' and pipeDelimited_True == [3,4,5]'
      ') else repr((form_False, form_True, spaceDelimited_False, spaceDelimited_True, '
      'pipeDelimited_False, pipeDelimited_True))',
    )

    response = self.publish(
      self.connector.getPath() + '/array?'
      + 'form_True=3&form_True=4&form_True=5&' + 'form_False=3,4,5&'
      + 'spaceDelimited_True=3&spaceDelimited_True=4&spaceDelimited_True=5&'
      + 'spaceDelimited_False=3%204%205&'
      + 'pipeDelimited_True=3&pipeDelimited_True=4&pipeDelimited_True=5&'
      + 'pipeDelimited_False=3|4|5')
    self.assertEqual(response.getBody(), b'"ok"')
    self.assertEqual(response.getStatus(), 200)


class TestOpenAPIParameterValidation(OpenAPIPetStoreTestCase):
  def assertValidationError(self, response, title, detail=None):
    body = json.loads(response.getBody())
    self.assertEqual(body['type'], 'parameter-validation-error')
    self.assertEqual(body['title'], title)
    if detail:
      self.assertEqual(body['detail'], detail)
    self.assertEqual(response.getStatus(), 400)

  def test_wrong_type_in_json_body(self):
    self.addPythonScript('TestPetStoreOpenAPI_updatePet', 'body', '')
    response = self.publish(
      self.connector.getPath() + '/pet',
      request_method='PUT',
      stdin=io.BytesIO(
        json.dumps(
          {
            "category": {
              "id": 1,
              "name": "Dogs"
            },
            "status": "available",
            "name": "doggie",
            "tags": [{
              "id": 0,
              "name": "string"
            }],
            "photoUrls": 123,  # wrong type
            "id": 10
          }).encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertValidationError(
      response,
      "Error validating request body: 123 is not of type 'array'",
      """\
123 is not of type 'array'

Failed validating 'type' in schema['properties']['photoUrls']:
    {'items': {'type': 'string', 'xml': {'name': 'photoUrl'}},
     'type': 'array',
     'xml': {'wrapped': True}}

On instance['photoUrls']:
    123""",
    )

  def test_wrong_type_in_path_param(self):
    self.addPythonScript('TestPetStoreOpenAPI_deletePet', 'petId', '')
    response = self.publish(
      self.connector.getPath() + '/pet/not_a_number', request_method='DELETE')
    self.assertValidationError(
      response,
      "Error validating parameter `petId`: 'not_a_number' is not of type 'integer'",
      """\
'not_a_number' is not of type 'integer'

Failed validating 'type' in schema:
    {'format': 'int64', 'type': 'integer'}

On instance:
    'not_a_number'""",
    )

  def test_wrong_type_in_query_param(self):
    self.addPythonScript('TestPetStoreOpenAPI_findPetsByStatus', 'status', '')
    response = self.publish(
      self.connector.getPath() + '/pet/findByStatus?status=invalid_status')
    self.assertValidationError(
      response,
      "Error validating parameter `status`: 'invalid_status' is not one of ['available', 'pending', 'sold']"
    )


class TestOpenAPINonAsciiParameters(OpenAPIPetStoreTestCase):
  def test_path_parameter(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_getUserByName',
      'username',
      'return "ok" if username == "hé" else repr(username)',
    )
    response = self.publish(self.connector.getPath() + '/user/hé')
    self.assertEqual(response.getBody(), b'"ok"')
    self.assertEqual(response.getStatus(), 200)

  def test_query_parameter(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_updatePetWithForm',
      'petId, name, status',
      'return "ok" if ('
      'petId == 789'
      ' and name == "é"'
      ' and status == "à"'
      ') else repr((petId, name, status))',
    )
    response = self.publish(
      self.connector.getPath() + '/pet/789?name=é&status=à',
      request_method='POST')
    self.assertEqual(response.getBody(), b'"ok"')
    self.assertEqual(response.getStatus(), 200)

    response = self.publish(
      self.connector.getPath() + '/pet/789?name=é', request_method='POST')
    self.assertEqual(response.getStatus(), 400)

  def test_request_body(self):
    # body is decoded as json, so strings are unicode on python2
    self.addPythonScript(
      'TestPetStoreOpenAPI_updatePet',
      'body',
      '# coding:utf-8\n'
      'return "ok" if body["name"] == u"héhé" else repr(body)',
    )
    response = self.publish(
      self.connector.getPath() + '/pet',
      request_method='PUT',
      stdin=io.BytesIO(
        json.dumps(
          {
            "category": {
              "id": 1,
              "name": "Dogs"
            },
            "status": "available",
            "name": "héhé",
            "tags": [{
              "id": 0,
              "name": "héhé"
            }],
            "photoUrls": ["héhé"],
            "id": 10
          }).encode()),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getBody(), b'"ok"')
    self.assertEqual(response.getStatus(), 200)

    response = self.publish(
      self.connector.getPath() + '/pet',
      request_method='PUT',
      stdin=io.BytesIO(b'"h\\u00e9h\\u00e9"'),
      env={'CONTENT_TYPE': 'application/json'})
    self.assertEqual(response.getStatus(), 400)


class TestOpenAPICommonParameters(OpenAPIPetStoreTestCase):
  _type_id = 'Test Open API Common Parameters'
  _open_api_schema = (
    '''
{
 "openapi": "3.0.3",
 "info": {
  "title": "TestOpenAPICommonParameters",
  "version": "0.0.0"
 },
 "paths": {
  '''

    # https://swagger.io/docs/specification/describing-parameters/#common-for-path
    '''
  "/common-for-path": {
   "parameters": [
    {
     "name": "a",
     "in": "query",
     "schema": {
      "type": "number"
     }
    }
   ],
   "get": {
    "operationId": "testGET1",
    "parameters": [
     {
      "name": "b",
      "in": "query",
      "schema": {
       "type": "number"
      }
     }
    ],
    "responses": {
     "200": {
      "description": "ok"
     }
    }
   }
  },'''

    # https://swagger.io/docs/specification/describing-parameters/#common-for-various-paths
    '''
  "/common-for-various-paths": {
   "get": {
    "operationId": "testGET2",
    "parameters": [
     {
      "name": "b",
      "in": "query",
      "schema": {
    '''

    # here we also excercice $refs in parameter schemas
    '''
       "$ref": "#/components/schemas/custom-number"
      }
     },
     {
      "$ref": "#/components/parameters/c"
     }
    ],
    "responses": {
     "200": {
      "description": "ok"
     }
    }
   }
  },
  '''

    # https://spec.openapis.org/oas/v3.1.0#fixed-fields-6
    # $refs: Allows for a referenced definition of this path item.
    # The referenced structure MUST be in the form of a Path Item Object.
    '''
  "/alias": {
   "$ref": "#/paths/~1common-for-path"
  }
 },
 "components": {
  "parameters": {
   "c": {
    "name": "c",
    "in": "query",
    "schema": {
     "type": "number"
    }
   }
  },
  "schemas": {
   "custom-number": {
    "type": "number"
   }
  }
 }
}
''')

  def test_common_for_path(self):
    self.addPythonScript(
      'TestOpenAPICommonParameters_testGET1',
      'a, b',
      'return "ok" if (a == 1 and b == 2) else repr((a, b))',
    )
    response = self.publish(
      self.connector.getPath() + '/common-for-path?a=1&b=2')
    self.assertEqual(response.getBody(), b'"ok"')

  def test_common_for_various_path(self):
    self.addPythonScript(
      'TestOpenAPICommonParameters_testGET2',
      'b, c',
      'return "ok" if (b == 2 and c == 3) else repr((b, c))',
    )
    response = self.publish(
      self.connector.getPath() + '/common-for-various-paths?b=2&c=3')
    self.assertEqual(response.getBody(), b'"ok"')

  def test_alias(self):
    self.addPythonScript(
      'TestOpenAPICommonParameters_testGET1',
      'a, b',
      'return "ok" if (a == 1 and b == 2) else repr((a, b))',
    )
    response = self.publish(self.connector.getPath() + '/alias?a=1&b=2')
    self.assertEqual(response.getBody(), b'"ok"')

  def test_getOpenAPIOperationIterator(self):
    # getOpenAPIOperationIterator iterates on the operations in order they are defined
    # in the json and resolve parameters.
    self.assertEqual(
      [
        (
          operation.path, operation.request_method,
          operation.get('operationId'),
          [p['name'] for p in operation.getParameters()]) for operation in
        self.portal.portal_types[self._type_id].getOpenAPIOperationIterator()
      ], [
        ('/common-for-path', 'get', 'testGET1', ['a', 'b']),
        ('/common-for-various-paths', 'get', 'testGET2', ['b', 'c']),
        ('/alias', 'get', 'testGET1', ['a', 'b'])
      ])


class TestOpenAPIMissingParameters(OpenAPIPetStoreTestCase):
  _type_id = 'Test Open API Missing Parameters'
  _open_api_schema = json.dumps(
    {
      'openapi': '3.0.3',
      'info': {
        'title': 'TestOpenAPIMissingParameters',
        'version': '0.0.0'
      },
      'paths': {
        '/query': {
          'get': {
            'operationId':
            'testGETQuery',
            'parameters': [
              {
                'name': 'user_id',
                'in': 'query',
                'required': True,
                'schema': {
                  'type': 'integer'
                }
              }
            ]
          }
        },
        '/query_with_default': {
          'get': {
            'operationId':
            'testGETQueryWithDefault',
            'parameters': [
              {
                'name': 'user_id',
                'in': 'query',
                'required': False,
                'schema': {
                  'default': 123,
                  'type': 'integer'
                }
              }
            ]
          }
        }
      }
    })

  def test_required_query(self):
    self.addPythonScript(
      'TestOpenAPIMissingParameters_testGETQuery',
      'user_id=None',
      'return user_id',
    )
    response = self.publish(self.connector.getPath() + '/query')
    self.assertEqual(
      json.loads(response.getBody()), {
        "status": 400,
        "type": "missing-parameter-error",
        "title": "user_id"
      })

    response = self.publish(self.connector.getPath() + '/query?user_id=')
    self.assertEqual(
      json.loads(response.getBody()), {
        "status": 400,
        "type": "missing-parameter-error",
        "title": "user_id"
      })

    response = self.publish(self.connector.getPath() + '/query?user_id')
    self.assertEqual(
      json.loads(response.getBody()), {
        "status": 400,
        "type": "missing-parameter-error",
        "title": "user_id"
      })

    response = self.publish(self.connector.getPath() + '/query?user_id=123')
    self.assertEqual(response.getBody(), b"123")
    self.assertEqual(response.getStatus(), 200)

  def test_required_query_with_default(self):
    self.addPythonScript(
      'TestOpenAPIMissingParameters_testGETQueryWithDefault',
      'user_id=None',
      'return user_id',
    )
    response = self.publish(
      self.connector.getPath() + '/query_with_default?user_id=789')
    self.assertEqual(response.getBody(), b"789")
    self.assertEqual(response.getStatus(), 200)

    response = self.publish(self.connector.getPath() + '/query_with_default')
    self.assertEqual(response.getBody(), b"123")
    self.assertEqual(response.getStatus(), 200)


class TestOpenAPIResponseContentType(OpenAPIPetStoreTestCase):
  def test_default_content_type(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_findPetsByStatus',
      'status',
      'return {"a": "b"}',
    )
    response = self.publish(
      self.connector.getPath() + '/pet/findByStatus?status=available')
    self.assertEqual(response.getHeader('Content-type'), 'application/json')
    self.assertEqual(response.getBody(), json.dumps({"a": "b"}).encode())
    self.assertEqual(response.getStatus(), 200)

  def test_content_type_set_by_script(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_findPetsByStatus',
      'status',
      'container.REQUEST.RESPONSE.setHeader("Content-Type", "text/html;charset=UTF-8")\n'
      'return "<h1>hello</h1>"',
    )
    response = self.publish(
      self.connector.getPath() + '/pet/findByStatus?status=available')
    self.assertEqual(
      response.getHeader('Content-type'), 'text/html;charset=UTF-8')
    self.assertEqual(response.getBody(), b"<h1>hello</h1>")
    self.assertEqual(response.getStatus(), 200)


class TestOpenAPIErrorHandling(OpenAPIPetStoreTestCase):
  def test_default_error_handler(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_findPetsByStatus',
      'status',
      '1//0',
    )
    response = self.publish(
      self.connector.getPath() + '/pet/findByStatus?status=available')
    self.assertEqual(response.getStatus(), 500)
    self.assertEqual(
      response.getBody(),
      json.dumps(
        {
          'type': 'unknown-error',
          'title': 'ZeroDivisionError: integer division or modulo by zero'
        }).encode())

  def test_transaction_abort_on_error(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_findPetsByStatus',
      'status',
      'context.getPortalObject().setTitle("ooops")\n'
      '1/0',
    )
    response = self.publish(
      self.connector.getPath() + '/pet/findByStatus?status=available',
      user='ERP5TypeTestCase')
    self.assertEqual(response.getStatus(), 500)
    self.assertNotEqual(self.portal.getTitle(), "ooops")

  def test_no_method_for_operation(self):
    response = self.publish(
      self.connector.getPath() + '/pet/findByStatus?status=available')
    self.assertEqual(
      response.getBody(),
      json.dumps(
        {
          'type':
          'no-method-for-operation',
          'title':
          'No method for operation findPetsByStatus GET /pet/findByStatus'
        }).encode())
    self.assertEqual(response.getStatus(), 500)

  def test_custom_error_handler(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_findPetsByStatus',
      'status',
      '1/0',
    )
    self.addPythonScript(
      'TestPetStoreOpenAPI_handleException',
      'exception, request',
      'request.RESPONSE.setStatus(410, lock=True)\n'
      'return "custom error" if isinstance(exception, ZeroDivisionError) else repr((exception, request))',
    )
    response = self.publish(
      self.connector.getPath() + '/pet/findByStatus?status=available')
    self.assertEqual(response.getBody(), b"custom error")
    self.assertEqual(response.getStatus(), 410)

  def test_custom_error(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_findPetsByStatus',
      'status',
      'from erp5.component.document.OpenAPITypeInformation import OpenAPIError\n'
      'class CustomError(OpenAPIError):\n'
      '  type = "custom-error-type"\n'
      '  status = 417\n'
      'raise CustomError("custom error title")',
    )
    response = self.publish(
      self.connector.getPath() + '/pet/findByStatus?status=available')
    self.assertEqual(
      response.getBody(),
      json.dumps(
        {
          'type': 'custom-error-type',
          'title': "custom error title",
          'status': 417
        }).encode())
    self.assertEqual(response.getStatus(), 417)

  def test_unauthorized(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_findPetsByStatus', 'status',
      'context.setTitle("ooops")')
    response = self.publish(
      self.connector.getPath() + '/pet/findByStatus?status=available')
    self.assertEqual(
      response.getBody(),
      json.dumps({
        'type': 'unauthorized',
      }).encode())
    self.assertEqual(response.getStatus(), 401)


class TestRestrictedAPI(OpenAPIPetStoreTestCase):
  _public_api = False
  def test_unauthorized(self):
    # the connector can not be traversed by anonymous user because the connector
    # is not public in this test.
    self.addPythonScript(
      'TestPetStoreOpenAPI_findPetsByStatus', 'status',
      'return "ok"')
    response = self.publish(
      self.connector.getPath() + '/pet/findByStatus?status=available')
    self.assertEqual(
      response.getBody(),
      json.dumps({
        'type': 'unauthorized',
      }).encode())
    self.assertEqual(response.getStatus(), 401)


class TestPathParameterAndAcquisition(OpenAPIPetStoreTestCase):
  """Check that path parameters works even when a Zope OFS document with
  same ID might be acquired.
  """
  def afterSetUp(self):
    super(TestPathParameterAndAcquisition, self).afterSetUp()
    if '789' not in self.portal.portal_web_services.objectIds():
      self.portal.portal_web_services.newContent(
        id='789',
        portal_type=self.portal.portal_web_services.allowedContentTypes()
        [0].getId())

  def test_get(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_getPetById',
      'petId',
      'return "ok" if petId == 789 else repr(petId)',
    )
    response = self.publish(self.connector.getPath() + '/pet/789')
    self.assertEqual(response.getBody(), b'"ok"')
    self.assertEqual(response.getStatus(), 200)

  def test_put(self):
    self.addPythonScript(
      'TestPetStoreOpenAPI_updateUser',
      'username',
      'return "ok" if username == "789" else repr(username)',
    )
    response = self.publish(
      self.connector.getPath() + '/user/789', request_method='PUT')
    self.assertEqual(response.getBody(), b'"ok"')
    self.assertEqual(response.getStatus(), 200)


class TestURLPathWithWebSiteAndVirtualHost(OpenAPIPetStoreTestCase):
  def afterSetUp(self):
    super(TestURLPathWithWebSiteAndVirtualHost, self).afterSetUp()
    self.web_site = self.portal.web_site_module.newContent(
      portal_type='Web Site')
    self.web_site.publish()
    self.web_section = self.web_site.newContent(portal_type='Web Section')
    self.web_section.publish()
    self.addPythonScript(
      'TestPetStoreOpenAPI_getPetById',
      'petId',
      'return "ok" if petId == 789 else repr(petId)',
    )

  def test_virtual_host(self):
    response = self.publish(
       '/VirtualHostBase/https/example.com:443/{}/VirtualHostRoot/{}/pet/789'.format(
        self.portal.getId(),
        self.connector.getRelativeUrl(),
    ))
    self.assertEqual(response.getBody(), b'"ok"')
    response = self.publish(
       '/VirtualHostBase/https/example.com:443/{}/VirtualHostRoot/_vh_vh1/_vh_vh2/{}/pet/789'.format(
        self.portal.getId(),
        self.connector.getRelativeUrl()
    ))
    self.assertEqual(response.getBody(), b'"ok"')

  def test_web_site(self):
    response = self.publish(
       '{}/{}/pet/789'.format(
        self.web_site.getPath(),
        self.connector.getRelativeUrl()
       ))
    self.assertEqual(response.getBody(), b'"ok"')

  def test_web_site_virtual_host(self):
    response = self.publish(
       '/VirtualHostBase/https/example.com:443/{}/VirtualHostRoot/{}/pet/789'.format(
        self.web_site.getPath(),
        self.connector.getRelativeUrl()
       ))
    self.assertEqual(response.getBody(), b'"ok"')
    response = self.publish(
       '/VirtualHostBase/https/example.com:443/{}/VirtualHostRoot/_vh_vh1/_vh_vh2/{}/pet/789'.format(
        self.web_site.getPath(),
        self.connector.getRelativeUrl()
       ))
    self.assertEqual(response.getBody(), b'"ok"')
    response = self.publish(
       '/VirtualHostBase/https/example.com:443/{}/VirtualHostRoot/{}/{}/pet/789'.format(
        self.portal.getId(),
        self.web_site.getRelativeUrl(),
        self.connector.getRelativeUrl()
       ))
    self.assertEqual(response.getBody(), b'"ok"')

  def test_web_section(self):
    response = self.publish(
       '{}/{}/pet/789'.format(
        self.web_section.getPath(),
        self.connector.getRelativeUrl()
       ))
    self.assertEqual(response.getBody(), b'"ok"')

  def test_web_section_virtual_host(self):
    response = self.publish(
       '/VirtualHostBase/https/example.com:443/{}/VirtualHostRoot/{}/pet/789'.format(
        self.web_section.getPath(),
        self.connector.getRelativeUrl()
       ))
    self.assertEqual(response.getBody(), b'"ok"')
    response = self.publish(
       '/VirtualHostBase/https/example.com:443/{}/VirtualHostRoot/_vh_vh1/_vh_vh2/{}/pet/789'.format(
        self.web_section.getPath(),
        self.connector.getRelativeUrl()
       ))
    self.assertEqual(response.getBody(), b'"ok"')
    response = self.publish(
       '/VirtualHostBase/https/example.com:443/{}/VirtualHostRoot/{}/{}/pet/789'.format(
        self.portal.getId(),
        self.web_section.getRelativeUrl(),
        self.connector.getRelativeUrl()
       ))
    self.assertEqual(response.getBody(), b'"ok"')

  def test_connector_virtual_host(self):
    response = self.publish(
       '/VirtualHostBase/https/example.com:443/{}/VirtualHostRoot/pet/789'.format(
        self.connector.getPath()
       ))
    self.assertEqual(response.getBody(), b'"ok"')
    response = self.publish(
       '/VirtualHostBase/https/example.com:443/{}/VirtualHostRoot/_vh_api/pet/789'.format(
        self.connector.getPath()
       ))
    self.assertEqual(response.getBody(), b'"ok"')

  def test_acquisition_path(self):
    response = self.publish(
       '/{}/person_module/{}/pet/789'.format(
        self.portal.getId(),
        self.connector.getRelativeUrl(),
    ))
    self.assertEqual(response.getBody(), b'"ok"')
    response = self.publish(
       '/VirtualHostBase/https/example.com:443/{}/VirtualHostRoot/person_module/{}/pet/789'.format(
        self.portal.getId(),
        self.connector.getRelativeUrl(),
    ))
    self.assertEqual(response.getBody(), b'"ok"')
    response = self.publish(
       '/VirtualHostBase/https/example.com:443/{}/VirtualHostRoot/_vh_vh1/_vh_vh2/person_module/{}/pet/789'.format(
        self.portal.getId(),
        self.connector.getRelativeUrl()
    ))
    self.assertEqual(response.getBody(), b'"ok"')


class TestOpenAPIRequestBody(OpenAPITestCase):
  _type_id = 'Test Open API Request Body'

  _open_api_schema = json.dumps(
    {
      'openapi': '3.0.3',
      'info': {
        'title': 'TestOpenAPIRequestBody',
        'version': '0.0.0'
      },
      'paths': {
        '/post': {
          'post': {
            'operationId': 'testPostByContentType',
            'requestBody': {
              'content': {
                'image/*': {
                  'schema': {
                    'type': 'string',
                    'format': 'binary',
                  }
                },
                'application/x-base64': {
                  'schema': {
                    'type': 'string',
                    'format': 'base64',
                  }
                }
              }
            }
          }
        }
      }
    })

  def test_request_body_content_encoding(self):
    self.addPythonScript(
      'TestOpenAPIRequestBody_testPostByContentType',
      'body=None',
      'container.REQUEST.RESPONSE.setHeader("Content-Type", "application/octet-stream")\n'
      'return body',
    )
    response = self.publish(
      self.connector.getPath() + '/post',
      request_method='POST',
      stdin=io.BytesIO(b'png file content'),
      env={"CONTENT_TYPE": 'image/png'})
    self.assertEqual(response.getBody(), b'png file content')
    self.assertEqual(response.getStatus(), 200)

    response = self.publish(
      self.connector.getPath() + '/post',
      request_method='POST',
      stdin=io.BytesIO(base64_encodebytes(b'base64 file content')),
      env={"CONTENT_TYPE": 'application/x-base64'})
    self.assertEqual(response.getBody(), b'base64 file content')
    self.assertEqual(response.getStatus(), 200)

    response = self.publish(
      self.connector.getPath() + '/post',
      request_method='POST',
      stdin=io.BytesIO(b'not base64'),
      env={"CONTENT_TYPE": 'application/x-base64'})
    self.assertEqual(response.getStatus(), 400)
    body = json.loads(response.getBody())
    self.assertEqual(body['type'], 'parameter-validation-error')
    self.assertIn('Error validating request body:', body['title'])
