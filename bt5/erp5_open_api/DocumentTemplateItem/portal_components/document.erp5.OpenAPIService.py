##############################################################################
# coding:utf-8
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
from __future__ import print_function

import itertools
import json

import jsonschema
import jsonpointer
import six
from six.moves import urllib

from AccessControl import ClassSecurityInfo
from AccessControl import ModuleSecurityInfo
from AccessControl.ZopeGuards import guarded_getattr
from ZPublisher.BaseRequest import DefaultPublishTraverse
from ZPublisher.interfaces import UseTraversalDefault
from zope.component import queryMultiAdapter
#from webdav.NullResource import NullResource

from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserPublisher

from zope.publisher.browser import BrowserView

import zope.component
import zope.interface

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject


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


class IOpenAPIRequest(zope.interface.Interface):  # pylint:disable=inherit-non-class
  """Marker interface to register error handler.
  """
@zope.component.adapter(Exception, IOpenAPIRequest)
class ErrorHandlerView(BrowserView):
  """On exception, delegate the rendering to OpenAPIService.handleException
  """
  def __call__(self):
    return self.__parent__.handleException(self.context, self.request)


zope.component.getGlobalSiteManager().registerAdapter(
  ErrorHandlerView,
  provided=zope.interface.Interface,
  name=u'index.html',
)


# IPublishTraverse seens unused XXX
@zope.interface.implementer(IPublishTraverse, IBrowserPublisher)
class OpenAPIWrapper(object):
  def __init__(self, context, request):
    self.context = context
    self.request = request
    zope.interface.alsoProvides(request, IOpenAPIRequest)

  def __getattr__(self, name):
    return getattr(self.context, name)

  def __getitem__(self, name):
    return self.context[name]

  # to disable webdav support returning NullResources on PUT request
  def __bobo_traverse__(self, request, name):
    raise KeyError(name)

  # XXX do not acquire 1 with
  # https://x.host.vifib.net/portal_web_services/5/pet/1?name=moko&status=pas%20l%C3%A0
  def publishTraverse(self, request, name):
    print('OpenAPIWrapper.publishTraverse', name)
    return self

  def browserDefault(self, request):
    print('OpenAPIWrapper.browserDefault')
    return OpenAPIBrowserView(self.context, request), ()


class OpenAPIBrowserView(BrowserView):
  """Render Open API operation calls
  """
  def __call__(self, *args, **kw):
    request = self.request
    context = self.context
    request_method = request.method.lower()

    #print(request.text())

    # we use absolute_url_path to support virtual hosts and also when on the context of a web site, for example:
    # https://erp5.example.com/web_site_module/renderjs_runner/portal_web_services/5/pet)
    request_path = request.physicalPathFromURL(
      request.get('URL'), )[1 + len(context.absolute_url_path().split('/')):]

    if context.getWebSiteValue():
      raise NotImplementedError()

    request_path = request.physicalPathFromURL(
      request.get('URL'), )[len(context.getPhysicalPath()):]

    parsed_qsl = urllib.parse.parse_qsl(request.environ['QUERY_STRING'], True)
    print(parsed_qsl)

    print("url", request.get('URL'))
    print("request_path", request_path)
    print("request_absolute_url_path", context.absolute_url_path())
    schema = context.getSchema()
    params = {}
    path_params = {}

    def validate_param(parameter_name, param_value, param_schema, full_schema):
      if param_schema is None:
        return param_value

      class with_schema_components(dict):
        # inject global `components` key from the schema so that
        # they can be resolved as $ref (using a dict subclass which will
        # not include it in the ParameterValidationError detail)
        def __missing__(self, key):
          if key == 'components':
            return full_schema[key]
          raise KeyError(key)

      try:
        jsonschema.validate(param_value, with_schema_components(param_schema))
      except jsonschema.ValidationError as e:
        raise ParameterValidationError(
          'Error validating {parameter_name}: {e}'.format(
            parameter_name=parameter_name, e=e.message), str(e))
      return param_value

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

    def iter_parameters(path_item, operation):
      for parameter in itertools.chain(path_item.get('parameters', ()),
                                       operation.get('parameters', ())):
        ref = parameter.get('$ref')
        if ref and ref[0] == '#':
          yield jsonpointer.resolve_pointer(schema, ref[1:])
        else:
          yield parameter

    def get_type(local_schema):
      if local_schema:
        if 'type' in local_schema:
          return local_schema['type']
        ref = local_schema['$ref']
        if ref and ref[0] == '#':
          return jsonpointer.resolve_pointer(schema, ref[1:], {}).get('type')

    # we order the methods to try to match the deepest "static" (ie. not variable)
    # path first: if we have have /pet/{petId} and /pet/findByStatus we want to
    # try /pet/findByStatus first. Luckyily a simple `sorted` is enough because
    # { sorts alphabetically after most paths elements
    for path, path_item in sorted(six.iteritems(schema['paths'])):
      definition_path = path.split('/')
      if definition_path[0] == '':
        definition_path = definition_path[1:]

      print(path, definition_path, request_path)
      if len(definition_path) == len(request_path):
        for definition_path_element, request_path_element in zip(
            definition_path, request_path):
          if not (definition_path_element[0] == "{"
                  or definition_path_element == request_path_element):
            break
          if definition_path_element[0] == "{" \
            and definition_path_element[-1] == "}":
            path_params[definition_path_element[1:-1]] = request_path_element
        else:
          # TODO: not needed
          request.other[(context, 'request_path')] = request_path

          operation = path_item.get(request_method, None)
          if operation is not None:
            for param_definition in iter_parameters(path_item, operation):
              print(param_definition)
              param_name = param_definition['name']
              param_in = param_definition['in']
              param_schema = param_definition.get('schema', {})
              if param_in == 'path':
                param_value = path_params[param_name]
                style = param_definition.get('style', 'simple')
                explode = param_definition.get('explode', False)
              elif param_in == 'query':
                style = param_definition.get('style', 'form')
                explode = param_definition.get('explode', True)
                param_value = []
                for k, v in parsed_qsl:
                  if k == param_name:
                    param_value.append(v)
                if len(param_value) == 1:
                  param_value = param_value[0]
              elif param_in == 'header':
                param_value = request.getHeader(param_name)
                style = param_definition.get('style', 'simple')
                explode = param_definition.get('explode', False)
              elif param_in == 'cookie':
                param_value = request.cookies.get(param_name)
                style = param_definition.get('style', 'form')
                explode = param_definition.get('explode', True)

              if not param_value:
                if param_definition.get('required'):
                  raise MissingParameterError(param_name)
                param_value = param_definition.get('default', param_value)
              else:
                print(
                  param_name, param_value, style, explode, param_definition)
                if get_type(param_schema) == 'array':
                  if not isinstance(param_value, list):
                    param_value = deserialize_array(
                      param_name,
                      param_value,
                      style,
                      explode,
                    )
                  if get_type(param_schema.get('items')) in ('integer',
                                                             'number'):
                    try:
                      param_value = [json.loads(item) for item in param_value]
                    except (TypeError, ValueError):
                      pass
                else:
                  param_value = deserialize_primitive_type(
                    param_name, param_value, style)
                  if get_type(param_schema) in ('integer', 'number'):
                    try:
                      param_value = json.loads(param_value)
                    except (TypeError, ValueError):
                      pass
                param_value = validate_param(
                  'Parameter ' + param_name,
                  param_value,
                  param_definition.get('schema'),
                  schema,
                )
              params[param_name] = param_value

            request_content_type = request.getHeader('content-type')
            request_body_definition = operation.get(
              'requestBody',
              {'content': {}})['content'].get(request_content_type, {})
            if request_body_definition:
              request_body = request.get('BODY') or ''
              if request_content_type == 'application/xml':
                raise NotImplementedError
              elif request_content_type == 'application/x-www-form-urlencoded':
                request_body = dict(urllib.parse.parse_qsl(request_body, True))
              elif request_content_type == 'application/json':
                request_body = json.loads(request_body)
              params['body'] = validate_param(
                'Request Body',
                request_body,
                request_body_definition.get('schema'),
                schema,
              )

            method = context.getMethodForOperation(
              path, request_method, operation.get('operationId'))
            print("ready to call", method, "with", params)
            if not method:
              raise NoMethodForOperationError(
                'No method for operation {operation_id} {request_method} {path}'
                .format(
                  operation_id=operation.get('operationId', ''),
                  request_method=request_method.upper(),
                  path=path,
                ))
            return method(**params)

    raise NotFound()


import logging
logger = logging.getLogger(__name__)


@zope.interface.implementer(IPublishTraverse)
class OpenAPIService(XMLObject):
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (
    PropertySheet.Base,
    PropertySheet.XMLObject,
    PropertySheet.CategoryCore,
    PropertySheet.DublinCore,
    PropertySheet.Account,
    PropertySheet.Arrow,
    PropertySheet.Reference,
  )

  security.declareProtected(
    Permissions.AccessContentsInformation, 'viewOpenAPIAsJson')

  def viewOpenAPIAsJson(self):
    """Return the Open API as JSON, with the current endpoint added as first servers
    """
    schema = self.getSchema()
    schema.setdefault('servers', []).insert(
      0, {
        'url': self.absolute_url(),
        'description': self.getDescription()
      })
    return json.dumps(schema)

  def handleException(self, exception, request):
    # Default Exception handler, renders the exception as json (rfc7807)
    # but make it possible to customize error handling with a type based
    # method.
    tbm = self.getTypeBasedMethod('handleException')
    if tbm:
      return tbm(exception, request)

    status = type(exception)
    if isinstance(exception, OpenAPIError):
      exception_info = {
        'type': exception.type,
        'title': exception.message,
      }
      if exception.status:
        status = exception_info['status'] = exception.status
      if exception.detail:
        exception_info['detail'] = exception.detail
    elif isinstance(exception, Unauthorized):
      # intentionnaly do not leak information when something is unauthorized
      exception_info = {
        'type': 'unauthorized',
      }
    elif isinstance(exception, NotFound):
      exception_info = {'type': 'not-found', 'title': str(exception)}
    else:
      exception_info = {
        'type': 'unknown-error',
        'title': '{}: {}'.format(type(exception).__name__, exception)
      }

    response = request.response
    response.setHeader("Content-Type", "application/json")
    response.setStatus(status, lock=True)
    response.setBody(json.dumps(exception_info).encode(), lock=True)

  def getMethodForOperation(self, path, http_method, operation_id):
    method_id = self.getTypeInfo().getMethodIdForOperation(
      path, http_method, operation_id)
    print('getMethodIdForOperation', method_id)
    if method_id:
      return guarded_getattr(self, method_id)
    return None

  def publishTraverse(self, request, name):
    try:
      return self._publishTraverse(request, name)
    except:
      logger.exception('wooops')
      raise

  def _publishTraverse(self, request, name):
    print(
      'OpenAPIService.publishTraverse', request.method, repr(request), name)
    if request.method.lower() not in ('get', 'post', 'head'):
      print('OpenAPIService.publishTraverse => returning a wrapper')
      return OpenAPIWrapper(self, request)
    adapter = DefaultPublishTraverse(self, request)
    print('OpenAPIService.adapter', adapter, 'name', name)
    try:
      obj = adapter.publishTraverse(request, name)
      print('OpenAPIService.obj', obj)
    except (KeyError, AttributeError):
      view = queryMultiAdapter((self, request), name=name)
      print('OpenAPIService.view', view, 'name', name)
      if view is not None:
        return view
      return OpenAPIWrapper(self, request)

    return obj

  def __bobo_traverse__(self, request, name):
    raise UseTraversalDefault

  def getSchema(self):
    return self.getTypeInfo().getSchema()
