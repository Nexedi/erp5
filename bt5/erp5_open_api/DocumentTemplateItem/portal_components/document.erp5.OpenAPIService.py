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

import base64
import binascii
import json
import typing
import six
from six.moves.urllib.parse import unquote

if typing.TYPE_CHECKING:
  from typing import Any, Callable, Optional
  from erp5.component.document.OpenAPITypeInformation import OpenAPIOperation, OpenAPIParameter
  from ZPublisher.HTTPRequest import HTTPRequest
  _ = (
    OpenAPIOperation, OpenAPIParameter, HTTPRequest, Any, Callable, Optional)

import jsonschema
from AccessControl import ClassSecurityInfo
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.component import queryMultiAdapter
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserPublisher
from ZPublisher.BaseRequest import DefaultPublishTraverse
from ZPublisher.interfaces import UseTraversalDefault
import zope.component
import zope.interface

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject

from erp5.component.document.OpenAPITypeInformation import (
  NoMethodForOperationError,
  OpenAPIError,
  ParameterValidationError,
  SchemaDefinitionError,
)


class IOpenAPIRequest(zope.interface.Interface):  # pylint:disable=inherit-non-class
  """Marker interface to register error handler for Open API requests.
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


@zope.interface.implementer(IPublishTraverse, IBrowserPublisher)
class OpenAPIWrapper(object):
  """Wrapper for traversal
  """
  def __init__(self, context, request):
    self.context = context
    zope.interface.alsoProvides(request, IOpenAPIRequest)
    # disable redirection to login page
    def unauthorized():
      raise Unauthorized()
    request.response.unauthorized = unauthorized

  def __getattr__(self, name):
    return getattr(self.context, name)

  def __getitem__(self, name):
    return self.context[name]

  def publishTraverse(self, request, name):
    return self

  def browserDefault(self, request):
    return OpenAPIBrowserView(self.context, request), ()


class OpenAPIBrowserView(BrowserView):
  """View to render Open API operation calls
  """
  def __call__(self, *args, **kw):
    return self.context.executeMethod(self.request)


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
    PropertySheet.Reference,
  )

  security.declareProtected(
    Permissions.AccessContentsInformation, 'viewOpenAPIAsJson')

  def viewOpenAPIAsJson(self):
    """Return the Open API as JSON, with the current endpoint added as first servers
    """
    schema = self.getTypeInfo().getSchema()
    schema.setdefault('servers', []).insert(
      0, {
        'url': self.absolute_url(),
        'description': self.getDescription()
      })
    return json.dumps(schema)

  def handleException(self, exception, request):
    """Default Exception handler, renders the exception as json (rfc7807)
    but make it possible to customize error handling with a type based
    method.
    """
    method = self.getTypeBasedMethod('handleException')
    if method:
      return method(exception, request)

    status = type(exception)
    if isinstance(exception, OpenAPIError):
      exception_info = {'type': exception.type, 'title': str(exception)}
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

  def getMatchingOperation(self, request):
    # type: (HTTPRequest) -> Optional[OpenAPIOperation]

    # Compute the relative URL of the request path, by removing the
    # relative URL of the Open API Service. This is tricky, because
    # it may be in the acquisition context of a web section and the request
    # might be using a virtual root with virtual paths.
    # First, strip the left part of the URL corresponding to the "root"
    web_section = self.getWebSectionValue()
    root = web_section if web_section is not None else self.getPortalObject()
    request_path_parts = [
      unquote(part) for part in request['URL']
      [1 + len(request.physicalPathToURL(root.getPhysicalPath())):].split('/')
    ]
    # then strip everything corresponding to the "self" open api service.
    # Here, unlike getPhysicalPath(), we don't use the inner acquistion,
    # but keep the acquisition chain from this request traversal.
    i = 0
    for aq_parent in reversed(self.aq_chain[:self.aq_chain.index(root)]):
      if aq_parent.id == request_path_parts[i]:
        i += 1
      else:
        break
    request_path_parts = request_path_parts[i:]

    request_method = request.method.lower()
    matched_operation = None
    for operation in self.getTypeInfo().getOpenAPIOperationIterator():
      if operation.request_method != request_method:
        continue
      operation_path_parts = operation.path.split('/')[1:]
      if len(operation_path_parts) != len(request_path_parts):
        continue
      if operation_path_parts == request_path_parts:
        # this is a concrete match, use this operation
        request.other['traverse_subpath'] = request_path_parts
        return operation

      # look for a templated match
      for operation_path_part, request_path_part in zip(
          operation_path_parts,
          request_path_parts,
      ):
        if operation_path_part == request_path_part:
          continue
        elif operation_path_part[0] == '{' and operation_path_part[-1] == '}':
          continue
        # TODO: match paths like /report.{format}
        else:
          break
      else:
        # we had a match, but there might be a "better" match, so we keep looping.
        # https://spec.openapis.org/oas/v3.1.0.html#patterned-fields :
        # > When matching URLs, concrete (non-templated) paths would be matched before
        # > their templated counterparts
        matched_operation = operation
        continue
    request.other['traverse_subpath'] = request_path_parts
    return matched_operation

  def getMethodForOperation(self, operation):
    # type: (OpenAPIOperation) -> Optional[Callable]
    operation_id = operation.get('operationId')
    if operation_id:
      method = self._getTypeBasedMethod(operation_id)
      if method is not None:
        return method
    raise NoMethodForOperationError(
      'No method for operation {operation_id} {request_method} {path}'.format(
        operation_id=operation.get('operationId', ''),
        request_method=operation.request_method.upper(),
        path=operation.path,
      ))

  def extractParametersFromRequest(self, operation, request):
    # type: (OpenAPIOperation, HTTPRequest) -> dict
    parameter_dict = {}
    for parameter in operation.getParameters():
      parameter_dict[parameter['name']] = self.validateParameter(
        'parameter `{}`'.format(parameter['name']),
        parameter.getValue(request),
        parameter,
        parameter.getJSONSchema(),
      )
    requestBody = self.validateRequestBody(
      operation.getRequestBodyValue(request),
      operation.getRequestBodyJSONSchema(request),
    )
    if requestBody:
      # we try to bind the request body as `body` parameter, but use alternate name
      # if it's already used by a parameter
      for body_arg in ('body', 'request_body', 'body_'):
        if body_arg not in parameter_dict:
          parameter_dict[body_arg] = requestBody
          break
      else:
        raise SchemaDefinitionError('unable to bind requestBody')
    return parameter_dict

  security.declareProtected(
    Permissions.AccessContentsInformation, 'validateParameter')

  def validateParameter(
      self, parameter_name, parameter_value, parameter, schema):
    # type: (str, Any, dict, dict) -> Any
    """Validate the parameter (or request body), raising a ParameterValidationError
    when the parameter is not valid according to the corresponding schema.
    """
    if schema is not None:
      if parameter_value is None and not parameter.get('required'):
        return parameter_value
      __traceback_info__ = (parameter_name, parameter_value, schema)
      try:
        jsonschema.validate(parameter_value, schema)
      except jsonschema.ValidationError as e:
        raise ParameterValidationError(
          'Error validating {parameter_name}: {e}'.format(
            parameter_name=parameter_name, e=e.message), str(e))
    return parameter_value

  security.declareProtected(
    Permissions.AccessContentsInformation, 'validateRequestBody')

  def validateRequestBody(self, parameter_value, schema):
    # type: (str, dict) -> Any
    """Validate the request body raising a ParameterValidationError
    when the parameter is not valid according to the corresponding schema.
    """
    if schema is not None:
      if schema.get('type') == 'string':
        if schema.get('format') == 'base64':
          try:
            return base64.b64decode(parameter_value)
          except (binascii.Error, TypeError) as e:
            if isinstance(e, TypeError):
              # BBB on python2 this raises a generic type error
              # but we don't want to ignore potential TypeErrors
              # on python3 here
              if six.PY3:
                raise
            raise ParameterValidationError(
              'Error validating request body: {e}'.format(e=str(e)))
        elif schema.get('format') == 'binary':
          return parameter_value or b''
    return self.validateParameter(
      'request body',
      parameter_value,
      {},
      schema,
    )

  def executeMethod(self, request):
    # type: (HTTPRequest) -> Any
    operation = self.getMatchingOperation(request)
    if operation is None:
      raise NotFound()
    method = self.getMethodForOperation(operation)
    parameters = self.extractParametersFromRequest(operation, request)
    result = method(**parameters)
    response = request.RESPONSE
    if response.getHeader('Content-Type'):
      return result
    response.setHeader("Content-Type", "application/json")
    return json.dumps(result).encode()

  def publishTraverse(self, request, name):
    if request.method.upper() in ('PUT', 'DELETE'):
      # don't use default traversal for PUT and DELETE methods, because they are
      # handled as WebDAV before the hooks are called.
      return OpenAPIWrapper(self, request)
    adapter = DefaultPublishTraverse(self, request)
    try:
      obj = adapter.publishTraverse(request, name)
    except (KeyError, AttributeError):
      view = queryMultiAdapter((self, request), name=name)
      if view is not None:
        return view
      return OpenAPIWrapper(self, request)
    return obj

  def __bobo_traverse__(self, request, name):
    raise UseTraversalDefault
