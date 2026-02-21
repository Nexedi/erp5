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
import traceback
import uuid

from jsonschema.validators import validator_for
from jsonschema import RefResolver

from AccessControl import ClassSecurityInfo, getSecurityManager
from zExceptions import Forbidden
from zLOG import LOG, WARNING


from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.CachePlugins.DistributedRamCache import\
  DistributedRamCache
from Products.ERP5Type.XMLObject import XMLObject
from erp5.component.module.JsonUtils import loadJson
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
class MCPService(XMLObject):
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

  def __call__(self, *args, **kw):
    request = self.REQUEST
    content_type = request.getHeader('Content-Type', '')
    if 'application/json' not in content_type:  # convenience for ERP5 users
      return XMLObject.__call__(self, *args, **kw)
    if self.getValidationState() != 'validated':
      request.response.setStatus(403)
      return ""
    request_method = request.method.lower()
    try:
      handler = getattr(self, "_handle%s" % request_method.capitalize())
    except AttributeError:
      request.response.setStatus(405)
      return ""
    return handler(request, *args, **kw)

  def _handlePost(self, request, *args, **kw):
    try:
      payload = loadJson(request.get('BODY'))
    except BaseException as e:
      raise JsonRpcParseError(str(e))
    response_data = self._processJsonRpcMessageOrBatch(payload, request)
    if response_data is not None:
      response = request.response
      response.setHeader("Content-Type", "application/json")
      response.setStatus(200, lock=True)
      response_data = _toUnicode(response_data)  # XXX
      return json.dumps(response_data, indent=2).encode()

  def _handleGet(self, request, *args, **kw):
    raise JsonRpcInternalError("GET requests not supported")  # TODO add resource

  # TODO By default DELETE should be allowed for authenticated users
  #   (yet it's not very urgent, session cache auto-cleans itself anyway)
  security.declareProtected(Permissions.DeletePortalContent, 'DELETE')
  def DELETE(self, REQUEST, RESPONSE):  # == _handleDelete (WebDav)
    """Delete session"""
    # NOTE WebDav methods have their own dedicated method handlers in Zope.
    if self.getValidationState() != 'validated':
      RESPONSE.setStatus(403)
      return ""
    if REQUEST.environ['REQUEST_METHOD'] != 'DELETE':
      raise Forbidden('REQUEST_METHOD should be DELETE.')
    session = self._getSession(REQUEST)
    user_id = self._getUserId()
    if user_id != session["user_id"]:
      raise Forbidden()
    self._delSession(session)
    RESPONSE.setStatus(204)
    return ""

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
        e = JsonRpcInternalError("Unexpected error: %s" % repr(e))
        msg = "%s: Unexpected Error: %s" % (msg_type, traceback.format_exc())
        LOG("MCPService._processJsonRpcMessage", WARNING, msg)
      e.request_id = message.get("id", None)
      return e.asjsonrpc()

  # NOTE This contains code not generally appliable for JSON-RPC, but specific for MCP
  def _processMCPMessage(self, message, request, msg_type):
    if msg_type == JsonRpcType.REQUEST:
      request_id = message["id"]
      if request_id is None:
        raise JsonRpcInvalidRequestError("Unlike base JSON-RPC, the ID MUST NOT be null.")
    method_name, params = message["method"], message.get("params", {})
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
      # MCP notifications do not require a session identifier per spec.
      # In this HTTP (stateless) implementation, we cannot determine which
      # session they belong to, so we accept them but do not process them.
      return None, None, None
    session = self._getSession(request)
    protocol_version = session['protocol_version']
    validator.validateMCPMessage(method_name, protocol_version, message, msg_type)
    try:
      norm_method_name = method_name.replace("/", "_").replace("-", "_")
      method = getattr(self, norm_method_name)
    except AttributeError:
      raise JsonRpcMethodNotFoundError("method '%s' not found" % method_name)
    # NOTE Currently there is no protection against concurrent requests
    # on the same session (e.g. on multiple zope nodes). MCP doesn't explicitly
    # enforces this, yet requests with side effects (e.g. tool calls) may be
    # indeterministic or give unexpected results when run concurrently.
    #
    # There are currently three options to prevent concurrent processings:
    #
    #   1. only using one zope node to process MCP requests
    #   2. specificing in load balancer to send requests with same
    #      MCP-Session-Id always to same zope node
    #   3. implement locking logic in zope (for instance through session, giving
    #      it a 'is_busy' attribute).
    #
    # NOTE In current implementations, concurrent calls of used tools is not
    # harmful, therefore no action is needed.
    result = method(session, **params)
    return result, session['id'], protocol_version

  def getValidator(self):
    try:
      return self._v_validator
    except AttributeError:
      v = self._v_validator = ProtocolValidator(self.getPortalObject())
      return v

  def _getSession(self, request):
    id_ = request.getHeader("MCP-Session-Id")
    if id_ is None:
      raise JsonRpcInvalidRequestError(
        "Request MUST specify 'MCP-Session-Id' in its header"
      )
    return self._getSessionFromId(id_)

  def _getSessionFromId(self, id_):
    storage_plugin = self._getPortalSessions()._getStoragePlugin()
    # NOTE Use plugin instead of portal_sessions[id] to avoid creating new
    # session if it doesn't exist yet
    cache_entry = storage_plugin.get(id_, 'SESSION', None)
    session = cache_entry.getValue() if cache_entry else None
    if not session:
      raise JsonRpcInvalidRequestError("invalid MCP session id '%s'" % id_)
    return session

  def _getPortalSessions(self):
    return self.getPortalObject().portal_sessions

  def _delSession(self, session):
    session.clear()

  def _getUserId(self):
    return getSecurityManager().getUser().getId()

  # MCP message processings
  def initialize(self, protocolVersion, capabilities, clientInfo, **kw):
    sessions = self._getPortalSessions()
    session_id = None
    while 1:
      session_id = uuid.uuid4().hex
      session = sessions[session_id]
      if not session:
        break
    session_data = dict(
      id=session_id,
      protocol_version=protocolVersion,
      client_info=clientInfo,
      user_id=self._getUserId(),
    )
    session.update(session_data)
    server_capabilities = dict(tools={"list": True, "call": True})
    server_info = {"version": "0.1", "name": "ERP5 MCP Server"}
    self._ensureDistributedCache()
    return dict(
      protocolVersion=protocolVersion,
      capabilities=server_capabilities,
      serverInfo=server_info,
    ), session_id, protocolVersion

  def _ensureDistributedCache(self):
    storage_plugin = self._getPortalSessions()._getStoragePlugin()
    if not isinstance(storage_plugin, DistributedRamCache):
      msg = "'portal_sessions' cache is not distributed. This may create issues"
      msg += " in case more than one Zope node is used to proceed MCP requests!"
      msg += " You may want to change 'portal_caches/erp5_session_cache' to "
      msg += " support safe multi-zope MCP Server usage!"
      LOG("MCPService._hookAfterLoad", WARNING, msg)

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
      output_schema = tool.getOutputSchema()
      tool = {
        "description": tool.getDescription(),
        "inputSchema": input_schema,
        "name": name,
        "title": title,
        "annotations": {
          "readOnlyHint": bool(tool.getReadOnly())
        },
      }
      if output_schema:
        tool["outputSchema"] = output_schema
      tool_list.append(tool)
    return dict(tools=tool_list)

  def tools_call(self, session, name, _meta=None, arguments=None, task=None):
    tool = self._getTool(name)
    output_schema = tool.getOutputSchema()
    is_error = False
    try:
      text, data = tool(**(arguments or {}))
    except Exception as e:
      if isinstance(e, JsonRpcError):
        raise
      msg = "tools/call/%s: Unexpected error: %s" % (name, traceback.format_exc())
      LOG("MCPService.tools_call", WARNING, msg)
      text, data = str(e), None
      is_error = True
    output = dict(isError=is_error, content=[{"type": "text", "text": text}])
    if output_schema and data is not None:
      output['structuredContent'] = data
    return output

  def _getTool(self, tool_name):
    portal_callables = self.getPortalObject().portal_callables
    try:
      return portal_callables[tool_name]
    except KeyError:
      raise JsonRpcInternalError("not found tool %s" % tool_name)


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

    erp5_mcp = self.portal.portal_skins["erp5_mcp"]
    def loadSchema(name):
      schema = str(erp5_mcp[name])
      return loadJson(schema)

    self.json_rpc_validator = {
      msg_type: _getValidator(loadSchema("JsonRpc2.0%sSchema" % msg_type.lower().capitalize()))
      for msg_type in (JsonRpcType.REQUEST, JsonRpcType.NOTIFICATION, JsonRpcType.RESPONSE)
    }
    self._mcp_registry = MCPProtocolRegistry(
      {proto: loadSchema("MCPSchema%s" % proto) for proto in SUPPORTED_MCP_PROTOCOL_VERSION_TUPLE})

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
    self._definition_key = "$defs" if "$defs" in schema else "definitions"
    self._method_index = _buildMCPIndex(schema)

  def __getitem__(self, definition_name):
    """Return validator for a specific schema definition."""
    try:
      return self._validator_cache[definition_name]
    except KeyError:
      pass
    defs = self._schema.get(self._definition_key, {})
    if definition_name not in defs:
      raise KeyError(definition_name)
    validator = _getValidator(
      {'$ref': '#/%s/%s' % (self._definition_key, definition_name)},
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
  defs = mcp_schema.get("$defs") or mcp_schema.get("definitions", {})
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
  return validator.validate


def _toUnicode(obj):
  if isinstance(obj, bytes):
    return obj.decode('utf-8', 'replace')
  elif isinstance(obj, dict):
    return {_toUnicode(k): _toUnicode(v) for k, v in obj.items()}
  elif isinstance(obj, list):
    return [_toUnicode(i) for i in obj]
  elif isinstance(obj, tuple):
    return tuple(_toUnicode(i) for i in obj)
  return obj