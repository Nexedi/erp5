# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2021-2026 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import json
import jsonschema
from erp5.component.module.JsonUtils import loadJson, fillDefaultJsonData
from erp5.component.document.JSONType import JSONType

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Utils import unicode2str

class JSONForm(JSONType):
  """
  Represents a form with JSON Form
  """
  meta_type = 'ERP5 Text Document'
  portal_type = 'JSON Form'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Version
                    , PropertySheet.Document
                    , PropertySheet.ExternalDocument
                    , PropertySheet.Url
                    , PropertySheet.TextDocument
                    , PropertySheet.Data
                    , PropertySheet.Reference
                    )

  def __call__(self, json_data, list_error=False, serialize=True): #pylint:disable=arguments-differ
    input_schema = self.getInputSchema()
    json_data = fillDefaultJsonData(input_schema, json_data)
    self.checkJSON(json_data, list_error, input_schema)
    method_id = self.getAfterMethodId()
    if not method_id:
      return "Nothing to do"
    method = getattr(getattr(self, 'aq_parent', None), method_id)
    result = method(json_data, self)
    output_schema = self.getOutputSchema()
    returns_json = self.getAfterMethodReturnsJson()
    parsed_result = None
    if output_schema is not None:
      parsed_result = loadJson(result) if returns_json else result
      self.checkJSON(parsed_result, list_error, output_schema)
    if not returns_json and serialize:
      return json.dumps(result)
    if returns_json and not serialize:
      return parsed_result if parsed_result is not None else loadJson(result)
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'checkJSON')
  def checkJSON(self, json_data, list_error=False, schema=None):
    """
    Validate contained JSON with the Schema defined in the Portal Type,
    raising an exception if invalid.
    """
    validation_result = self.validateJSON(json_data, list_error, schema)
    if validation_result is not True:
      if not list_error:
        raise jsonschema.exceptions.ValidationError(validation_result.message)
      else:
        raise ValueError(json.dumps(validation_result))

  security.declareProtected(Permissions.AccessContentsInformation, 'validateJSON')
  def validateJSON(self, json_data, list_error=False, schema=None):
    """
    Validate contained JSON with the Schema defined in the Portal Type.
    """
    defined_schema = schema or self.getInputSchema()
    try:
      jsonschema.validate(json_data, defined_schema, format_checker=jsonschema.FormatChecker())
    except jsonschema.exceptions.ValidationError as err:
      if list_error:
        validator = jsonschema.validators.validator_for(defined_schema)(defined_schema, format_checker=jsonschema.FormatChecker())
        return {
          unicode2str(defined_schema["$id"]): [
            ("Validation Error", x.message) for x in sorted(validator.iter_errors(json_data), key=lambda e: e.path)
          ]
        }
      return err
    return True

  security.declareProtected(Permissions.AccessContentsInformation, 'getInputSchema')
  def getInputSchema(self):
    return self._getSchema("TextContent")

  security.declareProtected(Permissions.AccessContentsInformation, 'getOutputSchema')
  def getOutputSchema(self):
    return self._getSchema("ResponseSchema")

  def _getSchema(self, key):
    schema = getattr(self, "get%s" % key)()
    return schema and loadJson(schema)
