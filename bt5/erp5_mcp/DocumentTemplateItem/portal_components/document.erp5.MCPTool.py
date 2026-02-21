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

import json

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass

from Products.ERP5.Document.PythonScript import PythonScript
from Products.ERP5Type import Permissions, PropertySheet

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

  def setParameterSignatureFromParameterList(self):
    parameter_list = []
    for parm in self.objectValues(sort_on=('int_index', 'ascending', 'int')):
      parameter_list.append(parm.getPythonArgumentString())
    self.setParameterSignature(", ".join(parameter_list))

  def getInputSchema(self):
    return _parametersToJsonschema(self.objectValues())

  # TODO currently output_schema is simply a property pointing to a text field
  #def getOutputSchema(self):
  #  return _signatureStrToJsonschema(self.getOutputSignature() or "")

  def __call__(self, *args, **kw):
    # Merge args into kw to allow schema validation
    kw = integrate_args_to_kw(self.getParameterSignature(), args, kw)
    input_schema = self.getInputSchema()
    try:
      validate(instance=kw, schema=input_schema)
    except Exception as e:
      raise TypeError(
        "input arguments don't match schema: %s" % str(e)
      )
    result = PythonScript.__call__(self, **kw)
    if isinstance(result, TEXT_TYPE_TUPLE):  # for tools without structured data
      result = (result, None)
    msg = "Tool '%s' returns bad return value: '%s' (type = '%s'). " % (
      self.getId(), result, type(result)
    )
    try:
      text, data = result
    except (TypeError, ValueError):
      msg += "Return value must be an iterable with two elements."
      raise JsonRpcInternalError(msg)
    if not isinstance(text, TEXT_TYPE_TUPLE):
      msg += "The first return value must be a string!"
      raise JsonRpcInternalError(msg)
    output_schema = self.getOutputSchema()
    if output_schema:
      output_schema = json.loads(output_schema)  # XXX could we directly store as JSON?
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


try:  # BBB: py2
  TEXT_TYPE_TUPLE = (str, unicode)
except NameError:
  TEXT_TYPE_TUPLE = (str,)


InitializeClass(MCPTool)  # XXX perhaps not needed


def integrate_args_to_kw(params, args, kw):
  """
  Map positional args to parameter names based on signature string

  Args:
    params: string like "a, b=10, c=None, **kw"
    args: tuple of positional arguments
    kw: dict of keyword arguments

  Returns:
    dict: Combined kwargs with args mapped to their parameter names
  """
  params = params.strip()
  if params == '':
    return kw.copy()
  param_list = [p.strip() for p in params.split(',')]
  regular_params = []
  kwargs_param = None
  for p in param_list:
    if p.startswith('**'):
      kwargs_param = p[2:].strip()
    else:
      regular_params.append(p)
  param_names = []
  defaults = {}
  for p in regular_params:
    if '=' in p:
      name, default = [part.strip() for part in p.split('=', 1)]
      param_names.append(name)
      defaults[name] = default
    else:
      param_names.append(p.strip())
  result = kw.copy()
  for i, arg_value in enumerate(args):
    if i < len(param_names):
      param_name = param_names[i]
      result[param_name] = arg_value
    else:
      if kwargs_param:
        result['arg_%d' % i] = arg_value
  return result


def _splitTopLevelComma(text):
  """Split `a, b[c, d], e` into top-level parts only."""
  result_list = []
  current_list = []
  depth = 0

  for char in text:
    if char == "[":
      depth += 1
      current_list.append(char)
    elif char == "]":
      depth -= 1
      if depth < 0:
        raise ValueError("Unbalanced closing bracket in type hint: %r" % text)
      current_list.append(char)
    elif char == "," and depth == 0:
      result_list.append("".join(current_list).strip())
      current_list = []
    else:
      current_list.append(char)

  if depth != 0:
    raise ValueError("Unbalanced brackets in type hint: %r" % text)

  tail = "".join(current_list).strip()
  if tail:
    result_list.append(tail)

  return result_list


def _parseGeneric(type_hint):
  """Return (base_type, [arg1, arg2, ...]) or (type_hint, None)."""
  type_hint = type_hint.strip()
  bracket_index = type_hint.find("[")

  if bracket_index < 0:
    return type_hint, None

  if not type_hint.endswith("]"):
    raise ValueError("Malformed generic type hint: %r" % type_hint)

  base_type = type_hint[:bracket_index].strip()
  inner_text = type_hint[bracket_index + 1:-1].strip()
  argument_list = _splitTopLevelComma(inner_text) if inner_text else []

  return base_type, argument_list


def _typeHintToJsonSchema(type_hint):
  """Convert a nested type hint string to JSON Schema.

  Supported:
    str
    int
    float
    number
    bool
    dict
    list
    list[str]
    list[list[str]]
    dict[str, int]
    dict[str, list[int]]

  Fallbacks:
    list -> {"type": "array", "items": {"type": "string"}}
    dict -> {"type": "object"}
    unknown -> {"type": "string"}
  """
  if not type_hint:
    return {"type": "string"}

  type_hint = type_hint.strip()
  lower_type_hint = type_hint.lower()

  simple_type_map = {
    "str": "string",
    "string": "string",
    "int": "integer",
    "integer": "integer",
    "float": "number",
    "number": "number",
    "bool": "boolean",
    "boolean": "boolean",
    "dict": "object",
    "object": "object",
  }

  if lower_type_hint in simple_type_map:
    return {"type": simple_type_map[lower_type_hint]}

  if lower_type_hint == "list":
    return {
      "type": "array",
      "items": {"type": "string"},
    }

  base_type, argument_list = _parseGeneric(type_hint)
  base_type_lower = base_type.lower()

  if base_type_lower == "list":
    if not argument_list:
      item_schema = {"type": "string"}
    elif len(argument_list) == 1:
      item_schema = _typeHintToJsonSchema(argument_list[0])
    else:
      raise ValueError("list[...] accepts exactly one type parameter: %r" % type_hint)

    return {
      "type": "array",
      "items": item_schema,
    }

  if base_type_lower == "dict":
    if not argument_list:
      return {"type": "object"}

    if len(argument_list) != 2:
      raise ValueError("dict[...] accepts exactly two type parameters: %r" % type_hint)

    key_type_hint, value_type_hint = argument_list  # pylint: disable=unpacking-non-sequence

    # JSON object keys are always strings.
    key_schema = _typeHintToJsonSchema(key_type_hint)
    if key_schema.get("type") != "string":
      raise ValueError(
        "JSON Schema object keys must be strings, got %r in %r"
        % (key_type_hint, type_hint)
      )

    return {
      "type": "object",
      "additionalProperties": _typeHintToJsonSchema(value_type_hint),
    }

  # Unknown generic/container type fallback
  return {"type": "string"}


# XXX can this be simplified with jsonschema package ?
def _parametersToJsonschema(parameters):
  schema = {
    "type": "object",
    "properties": {},
    "required": [],
    "additionalProperties": False,
  }

  for parameter in parameters:
    name = parameter.getReference()
    type_hint = parameter.getType()
    description = parameter.getDescription()

    param_schema = _typeHintToJsonSchema(type_hint)

    if description:
      param_schema["description"] = description

    schema["properties"][name] = param_schema

    try:
      parameter.getParameterDefaultValue()
    except ValueError:  # no default defined
      schema["required"].append(name)

  return schema