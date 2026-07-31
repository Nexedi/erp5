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

from jsonschema import validate
from jsonschema.exceptions import ValidationError
import six

from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass

from Products.ERP5.Document.PythonScript import PythonScript
from Products.ERP5Type import Permissions, PropertySheet

from erp5.component.module.JsonUtils import loadJson
from erp5.component.module.JsonRpc import (
  JsonRpcInternalError,
)


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

  def getInputSchema(self):
    return self._getSchema("TextContent")

  def getOutputSchema(self):
    return self._getSchema("ResponseSchema")

  def _getSchema(self, key):
    json_form = self.getSpecificationValue()
    if not json_form:
      return
    text = getattr(json_form, "get%s" % key)()
    if not text:
      return
    return loadJson(text)

  def setParameterSignatureFromSpecification(self):
    signature = json_schema_to_signature(self.getInputSchema())
    self.setParameterSignature(signature)

  def __call__(self, *args, **kw):
    # Merge args into kw to allow schema validation
    input_schema = self.getInputSchema()
    kw = integrate_args_to_kw(input_schema, args, kw)
    try:
      validate(instance=kw, schema=input_schema)
    except Exception as e:
      raise TypeError(
        "input arguments '%s' don't match schema: %s" % (kw, str(e))
      )
    result = PythonScript.__call__(self, **kw)
    if isinstance(result, six.string_types):  # for tools without structured data
      result = (result, None)
    msg = "Tool '%s' returns bad return value: '%s' (type = '%s'). " % (
      self.getId(), result, type(result)
    )
    try:
      text, data = result
    except (TypeError, ValueError):
      msg += "Return value must be an iterable with two elements."
      raise JsonRpcInternalError(msg)
    if not isinstance(text, six.string_types):
      msg += "The first return value must be a string!"
      raise JsonRpcInternalError(msg)
    output_schema = self.getOutputSchema()
    if output_schema:
      try:
        validate(instance=data, schema=output_schema)
      except ValidationError, e:
        raise JsonRpcInternalError(msg + "Output validation error: %s" % str(e))
    elif data is not None:
      raise JsonRpcInternalError(
        msg + "The second return value must be None if output schema is undefined!"
      )
    # If it's not an MCP call but a user testing a tool, just return the content
    if self.REQUEST is not None and self.REQUEST.method == "GET":
      return text
    return result


InitializeClass(MCPTool)  # XXX perhaps not needed


def integrate_args_to_kw(input_schema, args, kw):
  """Bind positional + keyword args using JSON schema"""
  properties = input_schema.get('properties', {})
  param_name_list = get_sorted_param_names(input_schema)
  result = {}
  for name, prop in properties.items():
    if 'default' in prop:
      result[name] = prop['default']
  for i, value in enumerate(args):
    if i < len(param_name_list):
      result[param_name_list[i]] = value
    else:
      result['arg_%d' % i] = value
  result.update(kw)
  return result


def json_schema_to_signature(schema):
  props = schema.get('properties', {})
  required = schema.get('required', [])
  param_name_list = get_sorted_param_names(schema)
  arg_list = []
  for param_name in param_name_list:
    if param_name in required:
      arg_list.append(param_name)
    else:
      prop = props[param_name]
      if isinstance(prop, dict) and 'default' in prop:
        default_val = prop['default']
        default_repr = repr(default_val)
      else:
        default_repr = 'None'
      arg_list.append('%s=%s' % (param_name, default_repr))
  # NOTE Return string with whitespace instead of empty string, because empty
  # string sets parameter signature to 'None' what could lead to subsequent
  # bugs (I run into an issue where PythonScript code assumed my tool had 1
  # argument, while in fact 'getParameterSignature' returned 'None').
  return ('%s' % ', '.join(arg_list)) or " "


def get_sorted_param_names(schema):
  """
  Return parameter names sorted by:
  1) required (no default) first
  2) optional (has default) after
  3) alphabetical within each group
  """
  properties = schema.get('properties', {})
  required_args = schema.get('required', [])
  required = []
  optional = []
  for name in properties.keys():
    if name in required_args:
      required.append(name)
    else:
      optional.append(name)
  required.sort()
  optional.sort()
  return required + optional
