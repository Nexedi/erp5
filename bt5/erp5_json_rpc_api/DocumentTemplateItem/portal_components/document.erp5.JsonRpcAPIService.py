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


# import base64
# import binascii
import json
import typing
# import six
from six.moves.urllib.parse import unquote

if typing.TYPE_CHECKING:
  from typing import Any, Callable, Optional
  from erp5.component.document.OpenAPITypeInformation import OpenAPIOperation, OpenAPIParameter
  from ZPublisher.HTTPRequest import HTTPRequest
  _ = (
    OpenAPIOperation, OpenAPIParameter, HTTPRequest, Any, Callable, Optional)

# import jsonschema
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from zExceptions import NotFound
from zope.publisher.interfaces import IPublishTraverse
import zope.component
import zope.interface

from Products.ERP5Type import Permissions, PropertySheet

from erp5.component.document.OpenAPITypeInformation import (
  byteify,
  OpenAPIError
)
from erp5.component.document.OpenAPIService import OpenAPIService
import jsonschema


class JsonRpcAPIError(OpenAPIError):
  pass

class JsonRpcAPINotParsableJsonContent(JsonRpcAPIError):
  type = "not-parsable-json-content"
  status = 400

class JsonRpcAPINotJsonDictContent(JsonRpcAPIError):
  type = "not-json-object-content"
  status = 400

class JsonRpcAPIInvalidJsonDictContent(JsonRpcAPIError):
  type = "invalid-json-object-content"
  status = 400

class JsonRpcAPINotAllowedHttpMethod(JsonRpcAPIError):
  type = "not-allowed-http-method"
  status = 405

class JsonRpcAPIBadContentType(JsonRpcAPIError):
  type = "unexpected-media-type"
  status = 415

ModuleSecurityInfo(__name__).declarePublic(
  JsonRpcAPIError.__name__,
  JsonRpcAPINotParsableJsonContent.__name__,
  JsonRpcAPINotJsonDictContent.__name__,
  JsonRpcAPIInvalidJsonDictContent.__name__,
  JsonRpcAPINotAllowedHttpMethod.__name__,
  JsonRpcAPIBadContentType.__name__,
)


@zope.interface.implementer(IPublishTraverse)
class JsonRpcAPIService(OpenAPIService):
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
    PropertySheet.Version,
  )

  def __getJsonFormListAsTuple(self):
    result_list = []
    for line in self.getJsonFormList():
      if not line:
        continue

      line_split_list = line.split(' | ', 1)
      if len(line_split_list) != 2:
        raise ValueError('Unparsable configuration: %s' % line)
      result_list.append(line_split_list)
    return result_list

  security.declareProtected(
    Permissions.AccessContentsInformation, 'viewOpenAPIAsJson')
  def viewOpenAPIAsJson(self):
    """Return the Open API as JSON, with the current endpoint added as first servers
    """
    result = {
      'openapi': '3.0.0',
      'info': {
        'version': self.getVersion('0.0.0'),
        'title': self.getTitle(),
        'description': self.getDescription()
      },
      'servers': [{
        'url': self.absolute_url()
      }]
    }
    path_dict = {}
    for action_reference, callable_id in self.__getJsonFormListAsTuple():
      json_form = getattr(self, callable_id)

      input_schema = json.loads(json_form.getTextContent())
      output_schema = json.loads(json_form.getResponseSchema() or '{}')

      path_dict['/%s' % action_reference] = {
        'post': {
          'requestBody': {
            'description': input_schema.get('description', ''),
            'content': {
              'application/json': {
                'schema': input_schema
              }
            }
          },
          'responses': {
            '200': {
              'description': output_schema.get('description', 'Successful operation'),
              'content': {
                'application/json': {
                  'schema': output_schema
                }
              }
            }
          }
        }
      }
    result['paths'] = path_dict
    return json.dumps(result, indent=2).encode()

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
    request.other['traverse_subpath'] = request_path_parts

    if request_path_parts:
      # Compare the request path with the web service configuration string
      # Do not expect any string convention here (like not / or whatever).
      # The convention is defined by the web service configuration only
      request_path = '/'.join(request_path_parts)
      matched_operation = None
      for action_reference, callable_id in self.__getJsonFormListAsTuple():
        if request_path == action_reference:
          matched_operation = callable_id

      if matched_operation is None:
        raise NotFound(request_path)

      content_type = request.getHeader('Content-Type', '')
      if 'application/json' not in content_type:
        raise JsonRpcAPIBadContentType(
          'Request Content-Type must be "application/json", not "%s"' % content_type
        )

      if (request_method != 'post'):
        raise JsonRpcAPINotAllowedHttpMethod('Only HTTP POST accepted')

    return matched_operation

  def executeMethod(self, request):
    # type: (HTTPRequest) -> Any
    operation = self.getMatchingOperation(request)
    if operation is None:
      raise NotFound()
    json_form = getattr(self, operation)#self.getMethodForOperation(operation)

    if json_form.getPortalType() != 'JSON Form':
      raise ValueError('%s is not a JSON Form' % operation)
    # parameters = self.extractParametersFromRequest(operation, request)
    try:
      json_data = byteify(json.loads(request.get('BODY')))
    except BaseException as e:
      raise JsonRpcAPINotParsableJsonContent(str(e))
    if not isinstance(json_data, dict):
      raise JsonRpcAPINotJsonDictContent("Did not received a JSON Object")

    try:
      result = json_form(json_data=json_data, list_error=False)#**parameters)
    except jsonschema.exceptions.ValidationError as e:
      raise JsonRpcAPIInvalidJsonDictContent(str(e))
    response = request.RESPONSE
    output_schema = json_form.getResponseSchema()
    # XXX Hardcoded JSONForm behaviour
    if (result == "Nothing to do") or (not result):
      # If there is no output, ensure no output schema is defined
      if output_schema:
        raise ValueError('%s has an output schema but response is empty' % operation)
      result = {
        'status': 200,
        'type': 'success-type',
        'title': 'query completed'
      }
    else:
      if not output_schema:
        raise ValueError('%s does not have an output schema but response is not empty' % operation)
      # Ensure the response matches the output schema
      try:
        jsonschema.validate(
          result,
          json.loads(output_schema),
          format_checker=jsonschema.FormatChecker()
        )
      except jsonschema.exceptions.ValidationError as e:
        raise ValueError(e.message)
    response.setHeader("Content-Type", "application/json")
    return json.dumps(result).encode()
