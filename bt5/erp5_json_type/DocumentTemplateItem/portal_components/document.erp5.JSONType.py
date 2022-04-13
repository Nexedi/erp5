# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
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
import zope.interface

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type import Permissions, PropertySheet

from erp5.component.interface.IJSONConvertable import IJSONConvertable

@zope.interface.implementer(
    IJSONConvertable,)
class JSONType(XMLObject):
  """
  Represents a portal type with JSON Schema
  """

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.TextDocument
                    )

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation, 'validateLocalJSONSchema')
  def validateLocalJSONSchema(self, list_error=False):
    """
    Validate contained JSON with the Schema defined in the Portal Type.
    """
    portal = self.getPortalObject()
    defined_schema = portal.portal_types[self.getPortalType()].getTextContent()
    text_content = self.asJSONText()
    if not defined_schema or text_content is None:
      # No errors if nothing is defined
      return True
    defined_schema = json.loads(defined_schema)
    current_schema = json.loads(text_content)
    try:
      jsonschema.validate(current_schema, defined_schema, format_checker=jsonschema.FormatChecker())
    except jsonschema.exceptions.ValidationError as err:
      if list_error:
        validator = jsonschema.validators.validator_for(defined_schema)(defined_schema, format_checker=jsonschema.FormatChecker())
        return sorted(validator.iter_errors(current_schema), key=lambda e: e.path)
      return err
    return True

  security.declareProtected(Permissions.AccessContentsInformation, 'validateJSONSchema')
  def validateJSONSchema(self, list_error=False):
    return self.validateLocalJSONSchema(list_error=list_error)

  security.declareProtected(Permissions.AccessContentsInformation, 'validateJsonSchema')
  def validateJsonSchema(self, list_error=False):
    # Deprecated, please use validateJSONSchema
    return self.validateJSONSchema(list_error=list_error)

  security.declareProtected(Permissions.AccessContentsInformation, 'asJSONText')
  def asJSONText(self):
    return self.getTextContent()

  security.declareProtected(Permissions.ModifyPortalContent, 'fromJSONText')
  def fromJSONText(self, json_text):
    return self.setTextContent(json_text)