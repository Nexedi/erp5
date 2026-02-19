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
import re
import typing

from jsonschema.validators import validator_for
from jsonschema import exceptions as jsonschema_exceptions, RefResolver
import six

if typing.TYPE_CHECKING:
  from typing import Any, Callable, Optional
  from erp5.component.document.OpenAPITypeInformation import OpenAPIOperation, OpenAPIParameter
  from ZPublisher.HTTPRequest import HTTPRequest
  _ = (
    OpenAPIOperation, OpenAPIParameter, HTTPRequest, Any, Callable, Optional)

from AccessControl import ClassSecurityInfo
from BTrees.OOBTree import OOBTree
from persistent import Persistent
from zope.publisher.interfaces import IPublishTraverse
import zope.component
import zope.interface

from Products.ERP5Type import Permissions, PropertySheet

from erp5.component.document.OpenAPIService import OpenAPIService
from erp5.component.module.JsonUtils import loadJson
from erp5.component.module.Log import log
from erp5.component.module.JsonRpc import (
  JsonRpcError,
  JsonRpcParseError,
  JsonRpcInvalidRequestError,
  JsonRpcMethodNotFoundError,
  # JsonRpcInvalidParamsError,
  JsonRpcInternalError,
  JsonRpcType
)


# NOTE The MCP protocol supports duplex JSON-RPC communication,
# meaning that both client and server may initiate requests.
#
# This implementation runs over standard Zope HTTP request/response,
# which is inherently stateless and does not provide a persistent
# bidirectional transport. As a result, the server cannot initiate
# JSON-RPC requests or notifications to the client.
#
# For typical AI-agent use cases (tools, prompts, resources), this is
# sufficient since the client initiates all interactions and the server
# only responds. Features that rely on server-initiated messages
# (e.g. progress notifications, streaming updates, or dynamic resource
# change events) are therefore not supported in this implementation.
@zope.interface.implementer(IPublishTraverse)
class MCPService(OpenAPIService):
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

  def __init__(self, *args, **kw):
    OpenAPIService.__init__(self, *args, **kw)
    # XXX how to GC idle sessions that aren't cleaned up by the client ?
    # => maybe sessions are small and infinite growth doesn't matter
    # => otherwise we may want to write a separate alarm that heuristically drops
    #    older sessions
    self._session_tree = OOBTree()

  def __call__(self, *args, **kw):
    request = self.REQUEST
    request_method = request.method.lower()
    try:
      handler = getattr(self, "_handle%s" % request_method.capitalize())
    except AttributeError:
      request.response.setStatus(405)
      return ""
    return handler(request)

  def _handlePost(self, request):
    try:
      payload = loadJson(request.get('BODY'))
    except BaseException as e:
      raise JsonRpcParseError(str(e))
    response_data = self._processJsonRpcMessageOrBatch(payload, request)
    if response_data is not None:
      log("response_data: %s" % response_data)
      response = request.response
      response.setHeader("Content-Type", "application/json")
      response.setStatus(200, lock=True)
      return json.dumps(response_data, indent=2).encode()

  def _handleGet(self, request):
    # TODO get resource
    return "get"

  def _handleDelete(self, request):
    # TODO gc / delete session
    return "delete"

  def _processJsonRpcMessageOrBatch(self, payload, request):
    if not isinstance(payload, list):
      return self._processJsonRpcMessage(payload, request)
    if not payload:
      return JsonRpcInvalidRequestError("empty batch").asjsonrpc()
    data = []
    for req in payload:
      response_data = self._processJsonRpcMessage(req, request)
      if response_data is not None:
        data.append(response_data)
    return data

  # NOTE This contains code to generally process JSON-RPC requests
  def _processJsonRpcMessage(self, message, request):
    try:
      msg_type = JsonRpcType.classify(message)
    except ValueError:
      return JsonRpcInvalidRequestError("could not classify msg type").asjsonrpc()
    try:
      validator = self.getValidator()
      validator.validateJsonRpcMessage(message, msg_type)
      response_data = self._processMCPMessage(message, request, msg_type)
      if msg_type == JsonRpcType.REQUEST:
        validator.validateJsonRpcMessage(response_data, JsonRpcType.RESPONSE, err=JsonRpcInternalError)
        return response_data
    except Exception as e:
      if not isinstance(e, JsonRpcError):
        # TODO Log unexpected error as warning !
        e = JsonRpcInternalError("Unexpected error: %s" % repr(e))
      e.request_id = message.get("id", None)
      #if isinstance(e, JsonRpcInternalError):
      #  log("%s: %s (%s)" % (self.getRelativeUrl(), e.message, e.data))
      log("%s: %s (%s)" % (self.getRelativeUrl(), e.message, e.data))
      return e.asjsonrpc()

  # NOTE This contains code not generally appliable for JSON-RPC, but specific for MCP
  def _processMCPMessage(self, message, request, msg_type):
    if msg_type == JsonRpcType.REQUEST:
      request_id = message["id"]
      if request_id is None:
        raise JsonRpcInvalidRequestError("Unlike base JSON-RPC, the ID MUST NOT be null.")
    method_name, params = message["method"], message.get("params", {})
    log("process %s: %s" % (method_name, message))
    validator = self.getValidator()
    # special case: neither session nor protocol specification exist yet
    if method_name == "initialize":
      result, session_id, protocol_version = self.initialize(**params)
    else:  # all other methods must be associated with a session + protocol version
      result, session_id, protocol_version = self.__processMCPMessage(
        message, request, msg_type, validator, method_name, params)
    if msg_type == JsonRpcType.REQUEST:
      validator.validateMCPMessage(
        method_name,
        protocol_version,
        result,
        JsonRpcType.RESPONSE,
        err=JsonRpcInternalError
      )
      request.response.setHeader("MCP-Session-Id", session_id)
      response_data = {"jsonrpc": "2.0", "result": result, "id": request_id}
      return response_data
    assert result is None, "%s must not return a result" % method_name

  def __processMCPMessage(self, message, request, msg_type, validator, method_name, params):
    if msg_type == JsonRpcType.NOTIFICATION:
      return None, None, None
    session_id = request.getHeader("MCP-Session-Id")
    if session_id is None:
      raise JsonRpcInvalidRequestError("messages must set 'MCP-Session-Id' in their header")
    try:
      session = self._session_tree[session_id]
    except KeyError:
      raise JsonRpcInvalidRequestError("invalid MCP session id '%s'" % session_id)
    protocol_version = session.protocol_version
    validator.validateMCPMessage(method_name, protocol_version, message, msg_type)
    try:
      norm_method_name = method_name.replace("/", "_").replace("-", "_")
      method = getattr(self, norm_method_name)
    except AttributeError:
      raise JsonRpcMethodNotFoundError("method '%s' not found" % method_name)
    # XXX Currently there is no protection against concurrent requests
    # on the same session (e.g. on multiple zope nodes). MCP doesn't explicitly
    # enforces this, yet requests with side effects (e.g. tool calls) may be
    # indeterministic or give unexpected results when run concurrently.
    #
    # There are currently three options to prevent concurrent processings:
    #
    #   1. only using one zope node to process MCP requests
    #   2. specificing in load balancer to send requests with same MCP-Session-Id always
    #      to same zope node
    #   3. implement locking logic in zope (for instance through ZODB, giving MCPSession a
    #      'is_busy' attribute).
    result = method(session, **params)
    return result, session_id, protocol_version
  
  def getValidator(self):
    try:
      return self._v_validator
    except AttributeError:
      v = self._v_validator = ProtocolValidator(self.getPortalObject())
      return v

  # MCP message processings
  def initialize(self, protocolVersion, capabilities, clientInfo, **kw):
    session_id = str(len(self._session_tree) + 1)
    server_capabilities = dict(tools={"list": True, "call": True}, prompts={}, resources={}, tasks={})
    server_info = {"version": "1.0", "name": "ERP5 MCP Server"}
    self._session_tree[session_id] = MCPSession(
      session_id, protocolVersion, clientInfo, capabilities, server_capabilities
    )
    return dict(
      protocolVersion=protocolVersion,
      capabilities=server_capabilities,
      serverInfo=server_info,
    ), session_id, protocolVersion

  def tools_list(self, session, _meta=None, cursor=None):
    tool_list = []
    for line in self.getToolList():
      if not line:
        continue
      try:
        title, name = line.split(" | ", 1)
      except ValueError:
        raise JsonRpcInternalError("bad tool configuration line: %s" % line)
      tool = self._getTool(name)
      input_schema = tool.getInputSchema()
      # TODO add output schema
      tool_list.append({
        "description": tool.getDescription(),
        "inputSchema": input_schema,
        "name": name,
        "title": title,
      })
    return dict(tools=tool_list)

  def tools_call(self, session, name, _meta=None, arguments=None, task=None):
    # TODO validate arguments against schema
    #   or should this be done by tool itself ?
    tool = self._getTool(name)
    is_error = False
    try:
      result = tool(**(arguments or {}))
    except Exception as e:
      result = str(e)
      is_error = True
    content = {"text": result, "type": "text"}
    return dict(content=[content], isError=is_error)

  def _getTool(self, tool_name):
    portal_callables = self.getPortalObject().portal_callables
    try:
      return portal_callables[tool_name]
    except KeyError:
      raise JsonRpcInternalError("not found tool %s" % tool_name)
      

class MCPSession(Persistent):
  def __init__(self, session_id, protocol_version, client_info, client_capabilities, server_capabilities, tools=None, resources=None, prompts=None):
    self.session_id = session_id
    self.protocol_version = protocol_version
    self.client_info = client_info
    self.client_capabilities = client_capabilities
    self.server_capabilities = server_capabilities
    self.tools = tools or {}
    self.resources = resources or {}
    self.prompts = prompts or {}
    # TODO Add principal_id -> erp5 user auth


SUPPORTED_MCP_PROTOCOL_VERSION_TUPLE = ("2025-03-26", "2025-06-18", "2025-11-25")
"""Lists all supported protocols.

Protocol Schema must be provided in 'portal_skins/erp5_mcp'.

This MCP Server implementation doesn't support pre-Streamable
HTTP transport (e.g. 2024-11-05 cannot be supported).
"""


class ProtocolValidator(object):
  """Facade responsible for validating incoming and outgoing protocol messages.

  This class validates:
    - Base JSON-RPC 2.0 messages
    - MCP protocol messages

  It loads JSON schemas from portal skins and delegates MCP validation
  to the version-specific registry.

  This class is stateless except for cached schema validators.
  """

  def __init__(self, portal):
    self.portal = portal
    self.json_rpc_validator = {
      msg_type: _getValidator(self._loadSchema("JsonRpc2.0%sSchema" % msg_type.lower().capitalize()))
      for msg_type in (JsonRpcType.REQUEST, JsonRpcType.NOTIFICATION, JsonRpcType.RESPONSE)
    }
    self._mcp_registry = MCPProtocolRegistry(
      {proto: self._loadSchema("MCPSchema%s" % proto) for proto in SUPPORTED_MCP_PROTOCOL_VERSION_TUPLE})
  
  def _loadSchema(self, name):
    schema = str(self.portal.portal_skins["erp5_mcp"][name])
    return json.loads(schema)

  def validateJsonRpcMessage(self, message, msg_type, err=JsonRpcInvalidRequestError):
    validator = self.json_rpc_validator[msg_type]
    try:
      validator(message)
    except Exception as e:
      raise err(e.message)

  def validateMCPMessage(self, method_name, protocol_version, message, msg_type, err=JsonRpcInvalidRequestError):
    validator = self._mcp_registry[protocol_version].getValidator(
      method_name, msg_type
    )
    try:
      validator(message)
    except Exception as e:
      raise err("Error when validating '%s' (%s): %s" % (
        method_name, msg_type, e.message))


class MCPProtocolRegistry(object):
  """Registry of MCP protocol schemas organized by protocol version.
   
  This class does not validate messages directly. It returns
  'MCPProtocolVersion' instances which perform the actual validation.
  """

  def __init__(self, schema_by_version):
    self._schema_by_version = schema_by_version
    self._version_cache = {}

  def __getitem__(self, version):
    """Return MCPProtocolVersion for the given protocol version."""
    try:
      return self._version_cache[version]
    except KeyError:
      pass
    try:
      schema = self._schema_by_version[version]
    except KeyError:
      raise JsonRpcInvalidRequestError("unsupported version %s" % version)
    version_obj = MCPProtocolVersion(schema)
    self._version_cache[version] = version_obj
    return version_obj


class MCPProtocolVersion(object):
  """Validator provider for a specific MCP protocol version."""

  def __init__(self, schema):
    """
    :param schema: JSON schema for this MCP protocol version
    """
    self._schema = schema
    self._resolver = RefResolver.from_schema(schema)
    self._validator_cache = {}
    self._method_index = _buildMCPIndex(schema)

  def __getitem__(self, definition_name):
    """Return validator for a specific schema definition."""
    try:
      return self._validator_cache[definition_name]
    except KeyError:
      pass
    defs = self._schema.get('$defs', {})
    if definition_name not in defs:
      raise KeyError(definition_name)
    validator = _getValidator(
      {'$ref': '#/$defs/%s' % definition_name},
      resolver=self._resolver
    )
    self._validator_cache[definition_name] = validator
    return validator

  def getValidator(self, method_name, msg_type):
    """Return validator for a specific MCP method and message type."""
    return self[self._getDefinitionName(method_name, msg_type)]
  
  def _getDefinitionName(self, method_name, msg_type):
    try:
      return self._method_index[(method_name, msg_type)]
    except KeyError:
      raise JsonRpcInvalidRequestError(
        "no schema for method '%s' and type '%s'"
        % (method_name, msg_type)
      )


def _buildMCPIndex(mcp_schema):
  index = {}
  defs = mcp_schema.get("$defs", {})
  for name, schema in defs.items():
    props = schema.get("properties", {})
    method = props.get("method", {})
    if not isinstance(method, dict) or "const" not in method:
      continue
    msg_type = (
      JsonRpcType.NOTIFICATION if name.endswith("Notification")
      else JsonRpcType.REQUEST if name.endswith("Request")
      else None
    )
    if msg_type is None:
      continue
    index[(method["const"], msg_type)] = name
    if msg_type == JsonRpcType.REQUEST:
      index[(method["const"], JsonRpcType.RESPONSE)] = "%sResult" % name[:-7]
  return index


def _getValidator(schema, *args, **kwargs):
  cls = validator_for(schema)
  cls.check_schema(schema)
  validator = cls(schema, *args, **kwargs)

  def _(instance):
    error = jsonschema_exceptions.best_match(validator.iter_errors(instance))
    if error is not None:
      if six.PY2:
        # Cleanup messages like
        #     "u'jsonrpc' is a required property"
        # to
        #     "jsonrpc' is a required property" 
        error.message = re.sub(r"u'([^']*)'", r"'\1'", error.message)
      raise error  # pylint: disable=raising-bad-type

  return _
