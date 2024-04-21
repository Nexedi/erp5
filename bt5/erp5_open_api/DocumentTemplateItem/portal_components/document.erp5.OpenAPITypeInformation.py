##############################################################################
#
# Copyright (c) 2023 Nexedi SA and Contributors. All Rights Reserved.
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

import collections
import json
import io
import itertools
import warnings
from six.moves import urllib

import typing
if typing.TYPE_CHECKING:
  from ZPublisher.HTTPRequest import HTTPRequest
  _ = (HTTPRequest, )

from AccessControl import ClassSecurityInfo
from AccessControl import ModuleSecurityInfo
import jsonpointer
import six

from Products.ERP5Type.ERP5Type import ERP5TypeInformation
from Products.ERP5Type import Permissions, PropertySheet


class OpenAPIError(Exception):
  """Base class for errors, the Open API Errors
  """
  type = None
  status = None

  def __init__(self, title, detail=None):
    super(OpenAPIError, self).__init__(title)
    self.detail = detail


class ParameterValidationError(OpenAPIError):
  """Error while validating request parameter.
  """
  type = "parameter-validation-error"
  status = 400


class MissingParameterError(OpenAPIError):
  """Parameter is missing
  """
  type = "missing-parameter-error"
  status = 400


class NoMethodForOperationError(OpenAPIError):
  """The service does not define a method for this operation.
  """
  type = "no-method-for-operation"


class SchemaDefinitionError(OpenAPIError):
  """Error in the definition of OpenAPI schema.
  """
  type = "schema-definition-error"


ModuleSecurityInfo(__name__).declarePublic(
  OpenAPIError.__name__,
  ParameterValidationError.__name__,
  MissingParameterError.__name__,
)

# On python2, make sure we use UTF-8 strings for the json schemas, so that we don't
# have ugly u' prefixes in the reprs. This also transforms the collections.OrderedDict
# to simple dicts, because the former also have an ugly representation.
# http://stackoverflow.com/a/13105359
if six.PY2:

  def byteify(string):
    if isinstance(string, dict):
      return {
        byteify(key): byteify(value)
        for key, value in string.iteritems()
      }
    elif isinstance(string, list):
      return [byteify(element) for element in string]
    elif isinstance(string, tuple):
      return tuple(byteify(element) for element in string)
    elif isinstance(string, six.text_type):
      return string.encode('utf-8')
    else:
      return string
else:

  def byteify(x):
    return x


class SchemaWithComponents(dict):
  # A local JSON schema ( for a parameter or request body ) with access to
  # global `components` to resolve $refs.
  __allow_access_to_unprotected_subobjects__ = 1

  def __init__(self, _schema, iterable):
    dict.__init__(self, byteify(iterable))
    self._schema = _schema

  def __missing__(self, key):
    if key == 'components':
      return byteify(self._schema[key])
    raise KeyError


class OpenAPIOperation(dict):
  __allow_access_to_unprotected_subobjects__ = True

  def __init__(self, _schema, _path, _request_method, _path_item, **kwargs):
    dict.__init__(self, **kwargs)
    self._schema = _schema
    self.path = _path
    self.request_method = _request_method
    self._path_item = _path_item

  def __str__(self):
    return '<OpenAPIOperation {} {} {}>'.format(
      self.get('operationId'),
      self.request_method,
      self.path,
    )

  def getParameters(self):
    # type: () -> Iterable[OpenAPIParameter]
    for parameter in itertools.chain(self._path_item.get('parameters', ()),
                                     self.get('parameters', ())):
      ref = parameter.get('$ref')
      if ref and ref[0] == '#':
        yield OpenAPIParameter(
          self._schema, self.path,
          **jsonpointer.resolve_pointer(self._schema, ref[1:]))
      else:
        yield OpenAPIParameter(self._schema, self.path, **parameter)

  def getRequestBodyValue(self, request):
    # type: (HTTPRequest) -> Any
    request_content_type = request.getHeader('content-type')
    request_body = request.get('BODY') or ''
    if request_content_type == 'application/xml':
      raise NotImplementedError
    elif request_content_type == 'application/x-www-form-urlencoded':
      request_body = dict(urllib.parse.parse_qsl(request_body, True))
    elif request_content_type == 'application/json':
      request_body = json.loads(request_body)
    return request_body

  def getRequestBodyJSONSchema(self, request):
    # type: (HTTPRequest) -> Optional[dict]
    """Returns the schema for the request body, or None if no `requestBody` defined
    """
    exact_request_content_type = request.getHeader('content-type')
    wildcard_request_content_type = '%s/*' % ((exact_request_content_type or '').split('/')[0])
    for request_content_type in exact_request_content_type, wildcard_request_content_type, '*/*':
      # TODO there might be $ref ?
      request_body_definition = self.get(
        'requestBody', {'content': {}})['content'].get(request_content_type)
      if request_body_definition:
        return SchemaWithComponents(
          self._schema, request_body_definition.get('schema', {}))


class OpenAPIParameter(dict):
  __allow_access_to_unprotected_subobjects__ = True

  def __init__(self, _schema, _path, **kwargs):
    dict.__init__(self, **kwargs)
    self._schema = _schema
    self._path = _path

  def _getType(self, local_schema):
    """Get the `type` key of a local schema, resolving refs in global schema if needed.
   """
    if local_schema:
      if 'type' in local_schema:
        return local_schema['type']
      if '$ref' in local_schema:
        ref = local_schema['$ref']
        if ref and ref[0] == '#':
          return jsonpointer.resolve_pointer(
            self._schema,
            ref[1:],
            {},
          ).get('type')

  def getValue(self, request):
    # type: (HTTPRequest) -> Any
    """Extract the value of this paremeter from request, returns
    the value, after trying to cast it to expected type.
    In case of errors during cast, the value is returned as is (typically as a str).
    """
    def deserialize_array(param_name, param_value, style, explode):
      # type: (str, str, str, bool) -> list[str]
      if style == 'simple':
        return param_value.split(',')
      if style == 'label':
        if param_value[0] != '.':
          raise ValueError(param_name, param_value)
        return param_value[1:].split('.' if explode else ',')
      if style == 'matrix':
        matrix_key = ";{param_name}=".format(param_name=param_name)
        if not param_value.startswith(matrix_key):
          raise ValueError(param_name, param_value)
        return param_value[len(matrix_key):].split(
          matrix_key if explode else ',')
      if style == 'form':
        return param_value.split(',')
      if style == 'spaceDelimited':
        return param_value.split(' ')
      if style == 'pipeDelimited':
        return param_value.split('|')
      raise SchemaDefinitionError(
        "Unsupported serialization style {style}".format(style=style))

    def deserialize_primitive_type(param_name, param_value, style):
      # type: (str, str, str) -> list[str]
      if style == 'label':
        if param_value[0] != '.':
          raise ValueError(param_name, param_value)
        return param_value[1:]
      if style == 'matrix':
        matrix_key = ";{param_name}=".format(param_name=param_name)
        if not param_value.startswith(matrix_key):
          raise ValueError(param_name, param_value)
        return param_value[len(matrix_key):]
      return param_value

    param_name = self['name']
    param_in = self['in']
    if param_in == 'path':
      param_value = None
      template = '{%s}' % param_name
      for path_element, request_path_element in zip(
          self._path.split('/')[1:], request.other['traverse_subpath']):
        if template in path_element:
          param_value = request_path_element
          break

      style = self.get('style', 'simple')
      explode = self.get('explode', False)
    elif param_in == 'query':
      style = self.get('style', 'form')
      explode = self.get('explode', True)
      param_value = []
      # Note that we parsed "again" QUERY_STRING and do not look in request.form
      # because request.form is set only for GET requests.
      parsed_qsl = urllib.parse.parse_qsl(
        request.environ['QUERY_STRING'], True)
      for k, v in parsed_qsl:
        if k == param_name:
          param_value.append(v)
      if len(param_value) == 1:
        param_value = param_value[0]
    elif param_in == 'header':
      param_value = request.getHeader(param_name)
      style = self.get('style', 'simple')
      explode = self.get('explode', False)
    elif param_in == 'cookie':
      param_value = request.cookies.get(param_name)
      style = self.get('style', 'form')
      explode = self.get('explode', True)

    if not param_value:
      if self.get('required'):
        raise MissingParameterError(param_name)
      param_value = self.get('schema', {}).get('default', param_value)
    else:
      parameter_type = self._getType(self.get('schema'))
      if parameter_type == 'array':
        if not isinstance(param_value, list):
          param_value = deserialize_array(
            param_name,
            param_value,
            style,
            explode,
          )
        if self._getType(self['schema'].get('items')) in ('integer', 'number'):
          try:
            param_value = [json.loads(item) for item in param_value]
          except (TypeError, ValueError):
            pass
      else:
        param_value = deserialize_primitive_type(
          param_name, param_value, style)
        if parameter_type in ('integer', 'number'):
          try:
            param_value = json.loads(param_value)
          except (TypeError, ValueError):
            pass

    return param_value

  def getJSONSchema(self):
    """Returns the schema for this parameter
    """
    return SchemaWithComponents(self._schema, self.get('schema', {}))


class OpenAPITypeInformation(ERP5TypeInformation):
  """
  """
  portal_type = 'Open API Type'
  meta_type = 'ERP5 Open API Type'

  # Default Properties
  property_sheets = (
    PropertySheet.Base,
    PropertySheet.XMLObject,
    PropertySheet.CategoryCore,
    PropertySheet.DublinCore,
    PropertySheet.Data,
    PropertySheet.TextDocument,
  )

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def getSchema(self):
    text_content = self.getTextContent() or '{}'
    if six.PY3:
      text_content = text_content.encode()
    stream = io.BytesIO(text_content)
    if self.getContentType() == 'application/x-yaml':
      try:
        import yaml  # pylint:disable=import-error
      except ImportError:
        warnings.warn(
          ImportWarning, "yaml not available, falling back to json")
      else:
        # XXX PyYAML does not seem to keep the order of keys on py2
        # ( https://gist.github.com/enaeseth/844388 could be a workaround )
        return yaml.load(stream, yaml.SafeLoader)
    if six.PY2:
      return json.load(stream, object_pairs_hook=collections.OrderedDict)
    else:
      return json.load(stream)

  security.declareProtected(
    Permissions.AccessContentsInformation, 'getOpenAPIOperationIterator')

  def getOpenAPIOperationIterator(self):
    # type: () -> typing.Iterator[OpenAPIOperation]
    """Iterator over the operations defined in the schema
    """
    schema = self.getSchema()

    http_verbs = {
      'get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace'
    }

    def iter_path_item(path, path_item):
      for request_method, operation in six.iteritems(path_item):
        if request_method == '$ref':
          if operation and operation[0] == '#':
            # BBB py2 yield from
            for _ in iter_path_item(
                path,
                jsonpointer.resolve_pointer(schema, operation[1:]),
            ):
              yield _

        if request_method in http_verbs:
          yield OpenAPIOperation(
            schema, path, request_method, path_item, **operation)

    for path, path_item in six.iteritems(schema.get('paths', {})):
      # BBB py2 yield from
      for _ in iter_path_item(path, path_item):
        yield _
