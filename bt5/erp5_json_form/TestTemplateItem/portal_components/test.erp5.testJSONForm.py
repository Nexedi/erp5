##############################################################################
#
# Copyright (c) 2002-2021 Nexedi SA and Contributors. All Rights Reserved.
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
from DateTime import DateTime
import six

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript

class Test(ERP5TypeTestCase):
  """
  A Sample Test Class
  """

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    # here, you can create the categories and objects your test will depend on
    self.createBasicScriptreturnJSONWithTimestamp()
    self.tic()

  def createBasicScriptreturnJSONWithTimestamp(
    self,
    name="ERP5Site_returnJSONWithTimestamp",
  ):
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      name,
      "text_data, form_reference",
      """
import json
return json.dumps({
  "datetime": DateTime().ISO8601(),
  "content": text_data,
}, indent=2)
"""
    )
    return name

  def fixJSONForm(self, reference, text_content="", after_method_id=""):
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
      text_content=text_content,
      after_method_id=after_method_id,
    )
    if self.portal.portal_workflow.isTransitionPossible(json_form, 'validate'):
      json_form.validate()

  def test_call_valid_json(self):
    """
    """
    schema = """{
	"$schema": "https://json-schema.org/draft/2019-09/schema",
  "$id": "my-schema.json",
    "properties":{
      "title": {
        "type": "string"
      }
    }
}"""
    data = {
	    "title": "foo"
    }
    method = "test_ERP5Site_processSimpleStriingAsJSON"
    after_method = self.createBasicScriptreturnJSONWithTimestamp()
    self.fixJSONForm(method, schema, after_method)
    self.tic()
    result = getattr(self.portal, method)(data)
    self.assertEqual(
      json.loads(result)['content'],
      json.loads(json.dumps(data))
    )

  def test_call_no_after_method_id_valid_json(self):
    """
    """
    schema = """{
	"$schema": "https://json-schema.org/draft/2019-09/schema",
  "$id": "my-schema.json",
    "properties":{
      "title": {
        "type": "string"
      }
    }
}"""
    data = {
	    "title": "foo"
    }
    method = "test_ERP5Site_processSimpleStriingAsJSON"
    self.fixJSONForm(method, schema, "")
    self.tic()
    result = getattr(self.portal, method)(data)
    self.assertEqual('Nothing to do', result)

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
    json_data = {
	"title": 2,
    "number": "2"
}
    method = "test_ERP5Site_processSimpleStriingAsJSON"
    after_method = self.createBasicScriptreturnJSONWithTimestamp()
    self.fixJSONForm(method, schema, after_method)
    self.tic()
    self.assertRaises(ValueError, getattr(self.portal, method), json_data, list_error=True)
    error = {"my-schema.json": [["Validation Error", "'2' is not of type 'integer'"], ["Validation Error", "2 is not of type 'string'"]]}
    if six.PY2:
      error = {"my-schema.json": [[u"Validation Error", u"'2' is not of type u'integer'"], [u"Validation Error", u"2 is not of type u'string'"]]}
    try:
      getattr(self.portal, method)(json_data, list_error=True)
      raise ValueError("No error raised during processing")
    except ValueError as e:
      self.assertEqual(error, json.loads(str(e)))

  def test_call_valid_datetime_format(self):
    """
    """
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
    data = {
    	"timestamp": DateTime().ISO8601()
    }
    method = "test_ERP5Site_processSimpleStriingAsJSON"
    after_method = self.createBasicScriptreturnJSONWithTimestamp()
    self.fixJSONForm(method, schema, after_method)
    self.tic()
    result = getattr(self.portal, method)(data)
    self.assertEqual(
      json.loads(json.dumps(data)),
      json.loads(result)['content']
    )

  def test_call_invalid_datetime_format(self):
    """
    """
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
    method = "test_ERP5Site_processSimpleStriingAsJSON"
    after_method = self.createBasicScriptreturnJSONWithTimestamp()
    self.fixJSONForm(method, schema, after_method)
    self.tic()
    self.assertRaises(ValueError, getattr(self.portal, method), json_data, list_error=True)
    error = {
      "my-schema.json": [[
        "Validation Error",  u"'2018-11-13T20:20:67' is not a 'date-time'"
      ]]
    }
    if six.PY2:
      error = {
        "my-schema.json": [[
          "Validation Error",  u"'2018-11-13T20:20:67' is not a u'date-time'"
        ]]
      }
    try:
      getattr(self.portal, method)(json_data, list_error=True)
      raise ValueError("No error raised during processing")
    except ValueError as e:
      self.assertEqual(error, json.loads(str(e)))

