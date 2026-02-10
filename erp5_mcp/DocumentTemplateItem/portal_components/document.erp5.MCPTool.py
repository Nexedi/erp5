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

import re

from AccessControl import ClassSecurityInfo
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

  def getInputSchema(self):
    return _signatureStrToJsonschema(self.getInputSignature() or "")
  
  def getOutputSchema(self):
    return _signatureStrToJsonschema(self.getOutputSignature() or "")


def _signatureStrToJsonschema(sig_str):
  """
  Convert a function signature string to JSON Schema.
  Example: "reference: str, first_name: str = None"

  Args:
    sig_str (str): Function parameter signature as a string.

  Returns:
    dict: JSON Schema representing the parameters.
  """
  schema = {"type": "object", "properties": {}, "required": []}

  # Split parameters by commas
  parts = [p.strip() for p in sig_str.split(",")]

  for part in parts:
    # Matches: name[: type][= default]
    m = re.match(r"(\w+)(\s*:\s*(\w+))?(\s*=\s*(.*))?", part)
    if not m:
      continue
    name, _, type_hint, _, default = m.groups()

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

    schema["properties"][name] = {"type": json_type}

    # Parameter is required if no default is specified
    if default is None:
      schema["required"].append(name)

  return schema