##############################################################################
#
# Copyright (c) 2002-2026 Nexedi SA and Contributors. All Rights Reserved.
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

from jsonschema.exceptions import ValidationError

from erp5.component.module.JsonUtils import loadJson
from DateTime import DateTime

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript


class Test(ERP5TypeTestCase):
  """
  Test JSON Form portal type.
  """

  default_input_schema = """{
  "$schema": "https://json-schema.org/draft/2019-09/schema",
  "$id": "my-schema.json",
    "properties":{
      "title": {
        "type": "string"
      }
    }
}"""

  default_output_schema = """{
  "$schema": "https://json-schema.org/draft/2019-09/schema",
  "$id": "my-schema.json",
  "type": "object",
  "properties": {
    "datetime": {
      "type": "string",
      "format": "date-time"
    },
    "content": {
      "type": "object"
    }
  },
  "required": [
    "datetime",
    "content"
  ]
}"""

  def afterSetUp(self):
    self.json_response_script_id = "ERP5Site_returnJSONWithTimestamp"
    self._createScript(
      self.json_response_script_id,
      """
import json
return json.dumps({
  "datetime": DateTime().ISO8601(),
  "content": text_data,
}, indent=2)
"""
    )
    self.object_response_script_id = "ERP5Site_returnObjectWithTimestamp"
    self._createScript(
      self.object_response_script_id,
      """
return {
  "datetime": DateTime().ISO8601(),
  "content": text_data,
}
"""
    )
    self.tic()
    self.default_json_form_reference = "test_ERP5Site_processSimpleStringAsJSON"

  def _createScript(self, name, code):
    createZODBPythonScript(
      self.portal.portal_skins.custom, name, "text_data, form_reference", code
    )

  def test_call_valid_json(self):
    self._assertValidJSONCall(self.json_response_script_id)

  def test_call_valid_json_unserialized(self):
    self._assertValidJSONCall(
      self.json_response_script_id,
      serialize=False,
    )

  def test_call_valid_json_after_method_returns_object(self):
    self._assertValidJSONCall(
      self.object_response_script_id,
      after_method_returns_json=False,
    )

  def test_call_valid_json_after_method_returns_object_unserialized(self):
    self._assertValidJSONCall(
      self.object_response_script_id,
      serialize=False,
      after_method_returns_json=False,
    )

  def test_call_no_after_method_id_valid_json(self):
    result = self._callJSONForm(
      {"title": "foo"},
      "",  # Empty script Id
    )
    self.assertEqual('Nothing to do', result)

  def test_call_valid_json_without_output_schema(self):
    self._assertValidJSONCall(self.json_response_script_id, output_schema="")

  def test_call_json_with_defaults(self):
    input_schema = """{
  "$schema": "https://json-schema.org/draft/2019-09/schema",
  "$id": "my-schema.json",
  "properties": {
    "title": {
      "type": "string",
      "default": "foo"
    }
  }
}"""
    result = self._callJSONForm(
      {}, self.json_response_script_id, input_schema=input_schema, serialize=0
    )
    self.assertEqual(result['content'], {"title": "foo"})

  def test_call_invalid_json_list_errors(self):
    """
    """
    schema = """{
	"$schema": "https://json-schema.org/draft/2019-09/schema",
  "$id": "my-schema.json",
    "properties":{
      "title": {
        "type": "string"
      },
      "number": {
        "type": "integer"
      }
    }
}"""
    json_data = {"title": 2, "number": "2"}
    self._fixJSONForm(schema, self.json_response_script_id)
    self.tic()
    self.assertRaises(
      ValueError,
      getattr(self.portal, self.default_json_form_reference),
      json_data,
      list_error=True
    )
    try:
      getattr(self.portal, self.default_json_form_reference)(
        json_data, list_error=True
      )
      raise ValueError("No error raised during processing")
    except ValueError as e:
      error_list = [["Validation Error", "'2' is not of type 'integer'"],
                    ["Validation Error", "2 is not of type 'string'"]]
      self.assertEqual({"my-schema.json": error_list}, loadJson(str(e)))

  def test_call_valid_datetime_format(self):
    schema = """{
	"$schema": "https://json-schema.org/draft/2019-09/schema",
  "$id": "my-schema.json",
    "properties":{
      "timestamp": {
        "type": "string",
        "format": "date-time"
      }
    }
}"""
    data = {"timestamp": DateTime().ISO8601()}
    self._assertValidJSONCall(
      self.json_response_script_id, data=data, input_schema=schema
    )

  def test_call_invalid_datetime_format(self):
    schema = """{
	"$schema": "https://json-schema.org/draft/2019-09/schema",
  "$id": "my-schema.json",
    "properties":{
      "timestamp": {
        "type": "string",
        "format": "date-time"
      }
    }
}"""
    json_data = {
	"timestamp": "2018-11-13T20:20:67"
}
    self._fixJSONForm(schema, after_method_id=self.json_response_script_id)
    self.tic()
    json_form = self._getDefaultJSONForm()
    self.assertRaises(ValueError, json_form, json_data, list_error=True)
    try:
      json_form(json_data, list_error=True)
      raise ValueError("No error raised during processing")
    except ValueError as e:
      error_list = [["Validation Error", "'2018-11-13T20:20:67' is not a 'date-time'"]]
      self.assertEqual({"my-schema.json": error_list}, loadJson(str(e)))

  def test_call_invalid_output_schema(self):
    output_schema = """{
  "$schema": "https://json-schema.org/draft/2019-09/schema",
  "$id": "my-schema.json",
  "type": "object",
  "properties": {
    "datetime": {
      "type": "string",
      "format": "date-time"
    }
  },
  "required": [
    "datetime"
  ],
  "additionalProperties": false
}"""

    def _(list_error=False):
      self._callJSONForm(
        {"title": "foo"},
        output_schema=output_schema,
        list_error=list_error,
        after_method_id=self.json_response_script_id,
      )

    self.assertRaises(ValidationError, _)
    try:
      _(True)
      raise ValueError("No error raised during processing")
    except ValueError as e:
      error_list = [[
        "Validation Error",
        "Additional properties are not allowed ('content' was unexpected)"
      ]]
      self.assertEqual({"my-schema.json": error_list}, loadJson(str(e)))

  def _assertValidJSONCall(
    self,
    after_method_id,
    serialize=True,
    after_method_returns_json=True,
    data=None,
    input_schema=None,
    output_schema=None,
  ):
    data = {"title": "foo"} if data is None else data
    result = self._callJSONForm(
      data,
      after_method_id,
      serialize=serialize,
      after_method_returns_json=after_method_returns_json,
      input_schema=input_schema,
      output_schema=output_schema,
    )
    content = loadJson(result)['content'] if serialize else result['content']
    self.assertEqual(content, loadJson(json.dumps(data)))

  def _callJSONForm(
    self,
    data,
    after_method_id=None,
    serialize=True,
    after_method_returns_json=True,
    input_schema=None,
    output_schema=None,
    list_error=False,
  ):
    self._fixJSONForm(
      input_schema,
      output_schema,
      after_method_id=after_method_id,
      after_method_returns_json=after_method_returns_json,
    )
    self.tic()
    json_form = self._getDefaultJSONForm()
    return json_form(data, serialize=serialize, list_error=list_error)

  def _fixJSONForm(
    self,
    input_schema="",
    output_schema=None,
    after_method_id="",
    after_method_returns_json=True,
    reference=None,
  ):
    if input_schema is None:
      input_schema = self.default_input_schema
    if output_schema is None:
      output_schema = self.default_output_schema
    if reference is None:
      reference = self.default_json_form_reference
    callables = self.portal.portal_callables
    json_form = callables.get(reference, None)
    if not json_form:
      json_form = callables.newContent(
        portal_type="JSON Form",
        title=reference,
        reference=reference,
        id=reference,
      )
    json_form.edit(
      text_content=input_schema,
      response_schema=output_schema,
      after_method_id=after_method_id,
      after_method_returns_json=after_method_returns_json,
    )
    if self.portal.portal_workflow.isTransitionPossible(json_form, 'validate'):
      json_form.validate()

  def _getDefaultJSONForm(self):
    return getattr(self.portal, self.default_json_form_reference)