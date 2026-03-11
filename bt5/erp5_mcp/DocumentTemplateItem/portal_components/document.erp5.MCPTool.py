##############################################################################
# coding:utf-8
# Copyright (c) 2026 Nexedi SA and Contributors. All Rights Reserved.
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


from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass

from Products.ERP5.Document.PythonScript import PythonScript
from Products.ERP5Type import Permissions, PropertySheet


class MCPTool(PythonScript):
  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (
    PropertySheet.Base,
    PropertySheet.XMLObject,
    PropertySheet.CategoryCore,
    PropertySheet.DublinCore,
    PropertySheet.PythonScript,
    PropertySheet.CatalogFilter,
    PropertySheet.MCPTool,
  )

  meta_type = 'ERP5 MCP Tool'
  portal_type = 'MCP Tool'
  add_permission = Permissions.AddPortalContent

  def setParameterSignatureFromParameterList(self):
    parameter_list = []
    for parm in self.objectValues(sort_on=('int_index', 'ascending', 'int')):
      parameter_list.append(parm.getPythonArgumentString())
    self.setParameterSignature(", ".join(parameter_list))

  def getInputSchema(self):
    return _parametersToJsonschema(self.objectValues())

  # TODO
  #def getOutputSchema(self):
  #  return _signatureStrToJsonschema(self.getOutputSignature() or "")


InitializeClass(MCPTool)  # XXX perhaps not needed


# XXX can this be simplified with jsonschema package ?
def _parametersToJsonschema(parameters):
  schema = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}

  for parameter in parameters:
    name = parameter.getReference()
    type_hint = parameter.getType()
    description = parameter.getDescription()

    # Map type hints to JSON Schema types
    json_type = "string"
    if type_hint:
      type_hint = type_hint.lower()
      if type_hint in ("int", "integer"):
        json_type = "integer"
      elif type_hint in ("float", "number"):
        json_type = "number"
      elif type_hint == "bool":
        json_type = "boolean"
      elif type_hint == "list":
        json_type = "array"
      elif type_hint == "dict":
        json_type = "object"

    param = {"type": json_type}
    if description:
      param["description"] = description

    schema["properties"][name] = param

    try:
      parameter.getParameterDefaultValue()
    except ValueError:  # no default defined
      schema["required"].append(name)

  return schema