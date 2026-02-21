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

import six

from jsonschema.validators import validator_for
from jsonschema import RefResolver

from AccessControl import ClassSecurityInfo, getSecurityManager
from zExceptions import Forbidden
from zLOG import LOG, INFO, WARNING


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
  JsonRpcInvalidParamsError,
  JsonRpcInternalError,
  JsonRpcType
)


SESSION_SCOPE = "SESSION"
"""Cache scope portal_sessions stores its sessions under."""


class MCPSessionError(JsonRpcInvalidRequestError):
  """A session error that the HTTP status code has to carry as well.

  Streamable HTTP defines how a client recovers from a session it can no longer
  use, and that definition keys entirely off the status code: 404 says the
  session is gone and the client MUST open a new one with initialize, 400 says
  it never sent a session id although the server requires one. Answering 200
  with nothing but a JSON-RPC error leaves a client no such signal -- it cannot
  tell an expired session from a malformed request, has no reason to
  re-initialize, and every tool call fails with 'Invalid Request' for the whole
  remaining lifetime of the connection.
  """

  def __init__(self, http_status, *args, **kw):
    JsonRpcInvalidRequestError.__init__(self, *args, **kw)
    self.http_status = http_status


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
      # A session error has to reach the client as the status its transport
      # defines for it (see MCPSessionError), not as a 200 it cannot act on.
      response.setStatus(request.other.pop("mcp_http_status", 200), lock=True)
      response_data = _toUnicode(response_data)  # XXX
      return json.dumps(response_data, indent=2).encode()

  def _handleGet(self, request, *args, **kw):
    # Streamable HTTP lets a client open an SSE stream with GET, so the server
    # can initiate messages on it. This implementation runs over stateless
    # Zope request/response and never initiates any (see the note on the
    # class), and what the transport asks of a server without a stream is 405
    # -- not an error the client has to interpret. Raising instead reached the
    # client as a JSON-RPC internal error and put a traceback in the event log
    # every time a client merely tried to open the stream.
    request.response.setHeader("Allow", "POST, DELETE")
    request.response.setStatus(405)
    return ""

  # TODO By default DELETE should be allowed for authenticated users
  #   (yet it's not very urgent, session cache auto-cleans itself anyway)
  # NOTE upstream uses Permissions.DeletePortalContent (a newer-core alias of
  # ModifyPortalContent); this instance's core predates it, so use the alias target.
  security.declareProtected(Permissions.ModifyPortalContent, 'DELETE')
  def DELETE(self, REQUEST, RESPONSE):  # == _handleDelete (WebDav)
    """Delete session"""
    # NOTE WebDav methods have their own dedicated method handlers in Zope.
    if self.getValidationState() != 'validated':
      RESPONSE.setStatus(403)
      return ""
    if REQUEST.environ['REQUEST_METHOD'] != 'DELETE':
      raise Forbidden('REQUEST_METHOD should be DELETE.')
    try:
      session = self._getSession(REQUEST)
    except MCPSessionError as e:
      # A client closing a session it has already lost is an ordinary race, not
      # a server error: answer with the status the transport defines instead of
      # letting the exception out as a 500 with a traceback in the event log.
      RESPONSE.setHeader("Content-Type", "application/json")
      RESPONSE.setStatus(e.http_status, lock=True)
      return json.dumps(e.asjsonrpc(), indent=2).encode()
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
      http_status = getattr(e, "http_status", None)
      if http_status is not None:
        # Picked up by _handlePost. In a batch the first such error decides:
        # every message of a batch travels on one session, so two of them
        # cannot disagree about its state.
        request.other.setdefault("mcp_http_status", http_status)
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
    self._touchSession(session)
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
      raise MCPSessionError(
        400, "Request MUST specify 'MCP-Session-Id' in its header"
      )
    return self._getSessionFromId(id_)

  def _getSessionFromId(self, id_):
    storage_plugin = self._getPortalSessions()._getStoragePlugin()
    # NOTE Use plugin instead of portal_sessions[id] to avoid creating new
    # session if it doesn't exist yet
    cache_entry = storage_plugin.get(id_, SESSION_SCOPE, None)
    session = cache_entry.getValue() if cache_entry else None
    if not session:
      raise MCPSessionError(404, "invalid MCP session id '%s'" % id_)
    return session

  def _touchSession(self, session):
    """Restart the expiry of a session that is being used.

    A session is written once, by initialize, and only read from then on. Its
    cache entry expires cache_duration after that one write -- a day with the
    stock erp5_session_cache -- no matter how busy the client is on it, because
    reading an entry never refreshes it (see DistributedRamCache.get). A
    long-running client therefore loses its session in the middle of its work,
    on the anniversary of its initialize and for no other reason. Storing the
    session again on every request that uses it makes the expiry count from the
    last use instead.
    """
    duration = getattr(session, 'session_duration', None)
    if not duration:
      # CacheEntry reads a missing duration as 'expired already', so with no
      # duration to restart from, leave the entry as it is.
      return
    storage_plugin = self._getPortalSessions()._getStoragePlugin()
    storage_plugin.set(session['id'], SESSION_SCOPE, session,
                       cache_duration=duration)

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
    server_capabilities = dict(
      tools={"list": True, "call": True},
      prompts={"listChanged": False},
      resources={"subscribe": False, "listChanged": False},
    )
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
    # A client is free to interpret the behaviour hints as it likes, including
    # in ways an operator does not want -- refusing a tool, or gating one
    # behind an approval it never asked for. Leaving them out per service puts
    # that decision back with whoever runs the service.
    omit_annotations = bool(self.getProperty('omit_tool_annotations', False))
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
      annotations = None if omit_annotations else _toolAnnotations(tool, title)
      tool = {
        "description": tool.getDescription(),
        "inputSchema": input_schema,
        "name": name,
        "title": title,
      }
      if annotations is not None:
        tool["annotations"] = annotations
      if output_schema:
        tool["outputSchema"] = output_schema
      tool_list.append(tool)
    return dict(tools=tool_list)

  def tools_call(self, session, name, _meta=None, arguments=None, task=None):
    # _getTool first so a wholly-unknown tool yields "not found tool" (-32603);
    # then enforce per-service scoping for tools that exist but aren't advertised.
    tool = self._getTool(name)
    if name not in self._getAdvertisedToolNames():
      raise JsonRpcInvalidParamsError(
        "tool '%s' is not available on this service" % name)
    output_schema = tool.getOutputSchema()
    arguments = _coerceArguments(tool.getInputSchema() or {}, arguments or {})
    call_id = self._startToolCallLog(name, arguments)
    try:
      result = self._callToolInHalContext(tool, arguments)
    except Exception as e:
      if isinstance(e, JsonRpcError):
        self._logToolCall(call_id, name, 'error',
                          '%s: %s' % (e.__class__.__name__, e))
        raise
      msg = "tools/call/%s: Unexpected error: %s" % (name, traceback.format_exc())
      LOG("MCPService.tools_call", WARNING, msg)
      self._logToolCall(call_id, name, 'error', msg)
      return dict(isError=True, content=[{"type": "text", "text": str(e)}])
    if self.getProperty('strip_personal_data', False):
      result = self._stripPersonalData(result, tool)
    # logged after stripping, on purpose -- see _logToolCall
    self._logToolCall(call_id, name, 'response', result)
    return _buildToolResult(result, output_schema)

  security.declarePrivate('_startToolCallLog')
  def _startToolCallLog(self, name, arguments):
    # Returns a short correlation id when call logging is on, else None (which
    # makes _logToolCall a no-op). The id ties a request line to its response
    # line: calls from several sessions interleave in the event log, and
    # without it a result cannot be matched to the arguments that produced it.
    if not self.getProperty('log_tool_calls', False):
      return None
    call_id = uuid.uuid4().hex[:8]
    self._logToolCall(call_id, name, 'request', arguments)
    return call_id

  security.declarePrivate('_logToolCall')
  def _logToolCall(self, call_id, name, phase, payload):
    """Write one leg of a tools/call to the Zope event log.

    Switched on per service with the log_tool_calls property.

    The response is logged *after* _stripPersonalData has run, deliberately:
    otherwise enabling call logging would write back into the event log
    precisely what personal-data stripping had just removed from the response,
    silently undoing that policy for anyone who can read the log.

    Arguments are logged as the client sent them. They are the caller's own
    input rather than records read out of ERP5, and redacting them would hide
    the very thing an operator switches this on to see -- but it does mean the
    event log becomes as sensitive as the queries being made against it.

    Payloads are truncated to log_tool_calls_max_length characters (0 for no
    limit): one erp5_read or erp5_search result can run to hundreds of
    kilobytes and would otherwise bury everything else in the log.
    """
    if call_id is None:
      return
    try:
      if isinstance(payload, tuple) and len(payload) == 2:
        # A tool returns (text, data) where text is already the JSON rendering
        # of data. Serialising the tuple as a whole escapes that text and
        # writes the payload twice over:
        #   ["{\"collected_count\": 11, ...}", {"collected_count": 11, ...}]
        # Keep the structured half, which serialises once and cleanly; fall
        # back to the text when a tool has no structured half to give.
        text, data = payload
        payload = data if data is not None else text
      if not isinstance(payload, six.string_types):
        # _toUnicode for the same reason as in _stripPersonalData: on Python 2
        # json.dumps(ensure_ascii=False) joins its chunks and dies on the first
        # umlaut when the payload mixes unicode with utf-8 str. default=repr
        # keeps a non-serialisable value from turning logging into an error.
        payload = json.dumps(_toUnicode(payload), ensure_ascii=False,
                             default=repr)
      limit = int(self.getProperty('log_tool_calls_max_length', 4000) or 0)
      if limit > 0 and len(payload) > limit:
        payload = '%s... [truncated, %s chars total]' % (payload[:limit],
                                                        len(payload))
      LOG("MCPService.tools_call", INFO,
          "[%s] %s %s %s" % (call_id, name, phase, payload))
    except Exception:
      # logging must never be the reason a tool call fails
      LOG("MCPService.tools_call", WARNING,
          "[%s] %s %s could not be logged: %s"
          % (call_id, name, phase, traceback.format_exc()))

  security.declarePrivate('_stripPersonalData')
  def _stripPersonalData(self, result, tool):
    # Redact personal data from a tool result before it reaches the MCP client
    # (GDPR). Called only when strip_personal_data is enabled. The field/type
    # policy is delegated to the skin script named by personal_data_policy_script
    # (default Base_stripPersonalData) so it is hot-editable without touching this
    # component. result shapes (see MCPTool.__call__ / _buildToolResult):
    #   (text, data) tuple  -> redact data, re-serialise text so both channels match
    #   list / {"content"}  -> rich/binary payload (e.g. erp5_download); passed
    #                          through as it is. File bytes cannot be
    #                          field-redacted, and withholding them blocked
    #                          downloading any document at all while stripping
    #                          was on, which is not the trade this policy is
    #                          meant to make. A file's contents are therefore
    #                          NOT redacted -- the policy covers the fields of
    #                          a record, not what is inside an attachment.
    #   bare string         -> no structured data to walk safely; withheld
    tool_id = tool.getId()
    if tool_id in self.getPersonalDataBlockedToolList():
      return ("Tool '%s' is disabled while personal-data stripping is active."
              % tool_id, None)
    policy_id = self.getProperty(
      'personal_data_policy_script', 'Base_stripPersonalData')
    policy = getattr(self, policy_id, None)
    if policy is None:
      LOG("MCPService._stripPersonalData", WARNING,
          "policy script '%s' not found; withholding result" % policy_id)
      return ("Personal-data policy script is missing; result withheld.", None)
    if isinstance(result, tuple) and len(result) == 2:
      text, data = result
      if data is None:
        return result
      data = policy(data)
      # json.dumps(ensure_ascii=False) joins its output chunks on Python 2, so
      # a payload mixing unicode with utf-8 str makes that join decode the
      # bytes as ascii and die on the first umlaut: "'ascii' codec can't decode
      # byte 0xc3". Every title read through Localizer is such a native str,
      # while everything the tools get back from getHateoas is unicode, so on a
      # localised instance this is the normal case rather than an edge one --
      # erp5_discover was unusable there while an English instance never saw it.
      return (json.dumps(_toUnicode(data), ensure_ascii=False), data)
    if isinstance(result, (list, dict)):
      return result
    if isinstance(result, six.string_types):
      return ("Result withheld while personal-data stripping is active.", None)
    return result

  def _getTool(self, tool_name):
    portal_callables = self.getPortalObject().portal_callables
    try:
      return portal_callables[tool_name]
    except KeyError:
      raise JsonRpcInternalError("not found tool %s" % tool_name)

  def _getAdvertisedToolNames(self):
    names = set()
    for line in self.getToolList():
      if line and " | " in line:
        names.add(line.split(" | ", 1)[1].strip())
    return names

  def _callToolInHalContext(self, tool, arguments):
    # Provide the HAL request context so restricted portal_callables tools may
    # call ERP5Document_getHateoas: the Hal skin (so it resolves to the right
    # script), Accept application/hal+json (else getHateoas 406s) and traversal
    # method GET. Setting request.other['method']='GET' also makes REQUEST.method read
    # 'GET', which would trip MCPTool's "user browser GET" branch and drop the data
    # channel; 'mcp_structured_call' tells MCPTool this is an MCP call so it keeps the
    # full (text, data) tuple and structuredContent survives.
    request = self.REQUEST
    skins = self.getPortalObject().portal_skins
    environ = request.environ
    saved_accept = environ.get('HTTP_ACCEPT')
    saved_method = request.other.get('method')
    saved_structured = request.other.get('mcp_structured_call')
    try:
      skins.changeSkin('Hal')
      environ['HTTP_ACCEPT'] = 'application/hal+json'
      request.other['method'] = 'GET'
      request.other['mcp_structured_call'] = 1
      return tool(**arguments)
    finally:
      if saved_accept is None:
        environ.pop('HTTP_ACCEPT', None)
      else:
        environ['HTTP_ACCEPT'] = saved_accept
      if saved_method is None:
        request.other.pop('method', None)
      else:
        request.other['method'] = saved_method
      if saved_structured is None:
        request.other.pop('mcp_structured_call', None)
      else:
        request.other['mcp_structured_call'] = saved_structured
      skins.changeSkin(skins.getDefaultSkin())

  def _iterPrompts(self):
    portal_callables = self.getPortalObject().portal_callables
    for prompt_id in sorted(portal_callables.objectIds()):
      if not prompt_id.startswith("prompt_"):
        continue
      prompt = portal_callables[prompt_id]
      try:
        if prompt.getPortalType() != "MCP Tool":
          continue
      except AttributeError:
        continue
      yield prompt_id, prompt

  def prompts_list(self, session, _meta=None, cursor=None):
    prompt_list = []
    for prompt_id, prompt in self._iterPrompts():
      schema = prompt.getInputSchema() or {}
      required = schema.get("required", [])
      arguments = []
      for arg_name, arg_def in schema.get("properties", {}).items():
        argument = {"name": arg_name, "required": arg_name in required}
        description = arg_def.get("description")
        if description:
          argument["description"] = description
        arguments.append(argument)
      prompt_list.append({
        "name": prompt_id,
        "title": prompt.getTitle() or prompt_id,
        "description": prompt.getDescription() or "",
        "arguments": arguments,
      })
    return dict(prompts=prompt_list)

  def prompts_get(self, session, name, _meta=None, arguments=None):
    portal_callables = self.getPortalObject().portal_callables
    if not name.startswith("prompt_") or name not in portal_callables.objectIds():
      raise JsonRpcInvalidParamsError("unknown prompt '%s'" % name)
    prompt = portal_callables[name]
    raw = self._callToolInHalContext(prompt, arguments or {})
    # A prompt MCP Tool may return either an MCP message list, or the (text, data)
    # tuple contract used by ordinary tools (then the text is one user message).
    if isinstance(raw, tuple):
      raw_messages = [{"role": "user", "content": raw[0]}]
    else:
      raw_messages = raw
    messages = []
    for message in raw_messages:
      content = message["content"]
      if isinstance(content, six.string_types):
        content = {"type": "text", "text": content}
      messages.append({"role": message["role"], "content": content})
    return dict(description=prompt.getDescription() or "", messages=messages)

  def resources_list(self, session, _meta=None, cursor=None):
    portal = self.getPortalObject()
    resources = []
    for module_id in sorted(portal.objectIds(spec=('ERP5 Folder',))):
      module = portal[module_id]
      title = module.getTitle() or module_id
      resources.append({
        "uri": "erp5://%s" % module_id,
        "name": module_id,
        "title": title,
        "description": "ERP5 module: %s" % title,
        "mimeType": "application/json",
      })
    return dict(resources=resources)

  def resources_templates_list(self, session, _meta=None, cursor=None):
    return dict(resourceTemplates=[{
      "uriTemplate": "erp5://{relative_url}",
      "name": "erp5_document",
      "title": "ERP5 document",
      "description": "Any ERP5 document addressed by its relative_url, e.g. erp5://person_module/1.",
      "mimeType": "application/json",
    }])

  def resources_read(self, session, uri, _meta=None):
    prefix = "erp5://"
    if not uri.startswith(prefix):
      raise JsonRpcInvalidParamsError("unsupported resource uri: %s" % uri)
    relative_url = uri[len(prefix):]
    portal = self.getPortalObject()
    # restrictedTraverse returns None in this direct component-method frame over the
    # HTTP POST dispatch (it resolves inside a PythonScript/tool frame); getitem does
    # resolve here (as resources_list relies on), so walk the path by getitem.
    document = portal
    try:
      for step in relative_url.split("/"):
        if step:
          document = document[step]
    except (KeyError, AttributeError, TypeError):
      document = None
    if document is None:
      raise JsonRpcInvalidParamsError("resource not found: %s" % uri)
    summary = {
      "relative_url": relative_url,
      "id": document.getId(),
      "portal_type": document.getPortalType(),
      "title": document.getTitle() or "",
    }
    for key, getter in (("description", "getDescription"),
                        ("simulation_state", "getSimulationState"),
                        ("validation_state", "getValidationState")):
      method = getattr(document, getter, None)
      if method is not None:
        try:
          value = method()
        except Exception:
          value = None
        if value:
          summary[key] = value
    text = json.dumps(summary, indent=2)
    return dict(contents=[{"uri": uri, "mimeType": "application/json", "text": text}])


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


def _hint(tool, property_name, default):
  # A hint is only ever advisory, so a tool that cannot answer for one must
  # not be able to break tools/list for every client.
  try:
    value = tool.getProperty(property_name, default)
  except Exception:
    return default
  return default if value is None else bool(value)


def _toolAnnotations(tool, title):
  """Behaviour hints a client uses to decide how to gate a tool.

  A hint left out is not "unknown" to a client: the protocol defines a default
  for each, and destructiveHint and openWorldHint both default to true.
  Advertising readOnlyHint alone therefore left every tool looking potentially
  destructive and open-world, and clients that classify tools from their
  annotations could not tell the reading tools from the writing ones. Emit the
  whole set instead.

  read_only decides the defaults; a tool may override the rest with a
  destructive / idempotent / open_world property -- e.g. an additive tool such
  as erp5_create, which writes but overwrites nothing.
  """
  read_only = bool(tool.getReadOnly())
  return {
    "title": title,
    "readOnlyHint": read_only,
    "destructiveHint": False if read_only else _hint(tool, "destructive", True),
    "idempotentHint": True if read_only else _hint(tool, "idempotent", False),
    "openWorldHint": _hint(tool, "open_world", False),
  }


def _buildToolResult(result, output_schema):
  # Shape a tool's return value into an MCP CallToolResult. Backward compatible
  # with the (text, data) contract, plus rich multi-modal content:
  #   list                -> used directly as the content-block array
  #                          (text/image/audio/resource_link/resource)
  #   dict with "content" -> a full CallToolResult envelope
  #                          (content [+ structuredContent] [+ isError] [+ _meta])
  #   (text, data) tuple  -> one text block (+ structuredContent when the tool declares
  #   or bare string         an output schema and returns non-None data)
  # The result is validated against CallToolResult by the response validator, so the
  # emitted content blocks must be legal for the negotiated protocol version.
  if isinstance(result, list):
    return {"isError": False, "content": result}
  if isinstance(result, dict) and "content" in result:
    output = {"isError": bool(result.get("isError", False)),
              "content": result["content"]}
    structured = result.get("structuredContent")
    if structured is not None:
      output["structuredContent"] = structured
    meta = result.get("_meta")
    if meta is not None:
      output["_meta"] = meta
    return output
  if isinstance(result, tuple):
    text, data = result
  else:
    text, data = result, None
  output = {"isError": False, "content": [{"type": "text", "text": text}]}
  if output_schema and data is not None:
    output["structuredContent"] = data
  return output


def _coerceScalar(value, json_type):
  if json_type == "integer":
    try:
      return int(value)
    except (TypeError, ValueError):
      return value
  if json_type == "number":
    try:
      return float(value)
    except (TypeError, ValueError):
      return value
  if json_type == "boolean":
    low = value.strip().lower()
    if low in ("true", "1", "yes", "on"):
      return True
    if low in ("false", "0", "no", "off", ""):
      return False
  if json_type == "string" and six.PY2 and isinstance(value, unicode):
    # py2 ERP5 code (e.g. getHateoas) mishandles unicode; hand tools native str.
    try:
      return value.encode("utf-8")
    except Exception:
      pass
  return value


def _coerceArguments(schema, arguments):
  properties = schema.get("properties", {})
  coerced = {}
  for key, value in arguments.items():
    prop = properties.get(key)
    if prop is not None and isinstance(value, six.string_types):
      coerced[key] = _coerceScalar(value, prop.get("type"))
    else:
      coerced[key] = value
  return coerced


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