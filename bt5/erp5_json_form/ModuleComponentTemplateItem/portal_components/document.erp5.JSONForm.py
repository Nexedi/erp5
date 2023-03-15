# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2021 Nexedi SA and Contributors. All Rights Reserved.
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
from erp5.component.document.JSONType import JSONType
from erp5.component.document.TextDocument import TextDocument

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet

class JSONForm(JSONType, TextDocument):
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

  def __call__(self, json_data, list_error=False): #pylint:disable=arguments-differ
    validation_result = self.validateJSON(json_data, list_error)
    if validation_result is not True:
      if not list_error:
        raise jsonschema.exceptions.ValidationError(validation_result.message)
      else:
        raise ValueError(json.dumps(validation_result))
    if self.getAfterMethodId():
      return getattr(getattr(self, 'aq_parent', None), self.getAfterMethodId())(json_data, self.getResponseSchema())
    return "Nothing to do"

  def validateJSON(self, json_data, list_error=False):
    """
    Validate contained JSON with the Schema defined in the Portal Type.
    """
    if not json_data:
      return True
    defined_schema = json.loads(self.getTextContent() or "")
    try:
      jsonschema.validate(json_data, defined_schema, format_checker=jsonschema.FormatChecker())
    except jsonschema.exceptions.ValidationError as err:
      if list_error:
        validator = jsonschema.validators.validator_for(defined_schema)(defined_schema, format_checker=jsonschema.FormatChecker())
        return {
          defined_schema["$id"]: [
            ("Validation Error", x.message) for x in sorted(validator.iter_errors(json_data), key=lambda e: e.path)
          ]
        }
      return err
    return True
