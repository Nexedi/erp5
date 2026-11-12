##############################################################################
#
# Copyright (c) 2026 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from contextlib import contextmanager
import io
import json

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

from erp5.component.module.JsonRpc import (
  JsonRpcType, JsonRpcInternalError, JsonRpcInvalidRequestError
)
from erp5.component.document.MCPService import _buildMCPIndex, ProtocolValidator


class MCPServiceApiTestMixin:
  """Tests MCP service API behavior."""

  def test_initialize(self):
    with self.connection():
      return  # initialize is called & tested when connection is created

  def test_initialize_unsupported_protocol_version(self):
    conn = MCPClientConnection(self)
    version = "2010-01-01"
    response = conn.initialize(
      protocolVersion=version,
      capabilities={},
      clientInfo={"version": 1.0, "name": "ERP5 MCP Test Client"},
    )
    data = "unsupported version %s" % version
    self.assertRpcError(response, -32600, "Invalid Request", data)

  def test_tools_list(self):
    with self.connection() as conn:
      self._test_tools_list(conn)

  def _test_tools_list(self, conn):
    response = conn.tools_list()
    info_list = self._fetchResult(response)["tools"]
    info_dict = {i["name"]: i for i in info_list}
    for t in self.tool_list:
      name = t.getReference()
      i = info_dict[name]
      self.assertEqual(i['inputSchema'], t.getInputSchema())
      if t.getOutputSchema():
        self.assertEqual(i['outputSchema'], t.getOutputSchema())
      self.assertEqual(i['annotations']['readOnlyHint'], t.getReadOnly())

  def test_tools_call(self):
    with self.connection() as conn:
      self._tc_ok(conn)
      self._tc_ok(conn, {"reference": "mcptesttestperson2"})  # no optional args
      self._tc_ok_structured(conn)
      self._tc_err_tool_runtime(conn)
      self._tc_err_missing_required_field(conn)
      self._tc_err_bad_parameter_type(conn)
      self._tc_err_non_existent_tool(conn)
      self._tc_err_missing_session_id(conn)

  def _tc_ok(self, conn, param_dict=None):
    param_dict = param_dict or self._test_person_data
    result = self._tools_call(conn, "mcptest_createPerson", param_dict)
    text = "Succesfully created person %s" % param_dict['reference']
    self.assertToolSuccess(result, text)
    self.assertPersonExists(param_dict)

  def _tc_ok_structured(self, conn):
    d = self._test_person_data
    param_dict = dict(reference=d['reference'])
    result = self._tools_call(conn, "mcptest_readPerson", param_dict)
    self.assertFalse(result["isError"])
    data = {"persons": [d]}
    self.assertEqual(result["structuredContent"], data)
    text = "; ".join("%s: %s" % (k, d[k]) for k in sorted(d))
    self.assertEqual(result["content"][0]["text"], text)

  def _tc_err_tool_runtime(self, conn):
    """Test error in tool code itself"""
    param_dict = self._test_person_data
    result = self._tools_call(conn, "mcptest_createPerson", param_dict)
    m = 'Could not create person: The id '
    m += '"%s" is invalid - it is already in use.' % param_dict["reference"]
    self.assertToolError(result, equals=m)

  def _tc_err_missing_required_field(self, conn):
    result = self._tools_call(conn, "mcptest_createPerson", {})
    m = "input arguments '{}' don't match schema: 'reference' is a required property"
    self.assertToolError(result, contains=[m])

  def _tc_err_bad_parameter_type(self, conn):
    param_dict = dict(reference="t", first_name=["bad_type"])
    result = self._tools_call(conn, "mcptest_createPerson", param_dict)
    m = [
      "input arguments '%s' don't match schema" % repr(param_dict),
      "is not of type 'string'"
    ]
    self.assertToolError(result, contains=m)

  def _tc_err_non_existent_tool(self, conn):
    tool_name = "mcptest_nonExistentTool"
    response = conn.tools_call(name=tool_name, arguments={})
    data = "not found tool %s" % tool_name
    self.assertRpcError(response, -32603, "Internal error", data)

  def _tc_err_missing_session_id(self, conn):
    session_id, conn.session_id = conn.session_id, None
    param_dict = dict(reference=self._test_person_data['reference'])
    response = conn.tools_call(
      name="mcptest_readPerson", arguments=param_dict
    )
    data = "Request MUST specify 'MCP-Session-Id' in its header"
    self.assertRpcError(response, -32600, "Invalid Request", data)
    conn.session_id = session_id  # restore state

  _test_person_data = dict(
    reference="mcptest_test_person",
    first_name="first name test",
    last_name="last name test",
  )

  def test_undefined_method(self):
    with self.connection() as conn:
      cmd = "not/existent/command"
      response = conn.sendRequest(cmd, {})
      data = "no schema for method 'not/existent/command' and type 'request'"
      self.assertRpcError(response, -32600, "Invalid Request", data)

  def test_invalid_session_id(self):
    conn = MCPClientConnection(self)
    conn.session_id = 2**128
    response = conn.tools_list()
    data = "invalid MCP session id '%s'" % conn.session_id
    self.assertRpcError(response, -32600, "Invalid Request", data)

  def test_concurrent_sessions(self):
    with self.connection() as conn1:
      with self.connection() as conn2:
        self.assertNotEqual(conn1.session_id, conn2.session_id)
        self._test_tools_list(conn1)
        self._test_tools_list(conn2)

  def test_jsonrpc_batch_request(self):
    with self.connection() as conn:
      batch = []
      param_dict_list = [dict(reference=r) for r in ("tbatch0", "tbatch1")]
      for param_dict in param_dict_list:
        t = JsonRpcType.REQUEST
        params = dict(name="mcptest_createPerson", arguments=param_dict)
        msg = conn.constructJsonRpcMessage("tools/call", params, t)
        batch.append(msg)
      response = conn._sendMessage(batch, t)
      data_list = json.loads(response.getBody())
      for data, param_dict in zip(data_list, param_dict_list):
        result = data["result"]
        text = "Succesfully created person %s" % param_dict['reference']
        self.assertToolSuccess(result, text)
      self.tic()
      for param_dict in param_dict_list:
        self.assertPersonExists(param_dict)

  def test_jsonrpc_no_id(self):
    with self.connection() as conn:
      m = conn.constructJsonRpcMessage("tools/list", {}, JsonRpcType.REQUEST)
      m["id"] = None
      response = conn._sendMessage(m, JsonRpcType.REQUEST)
      data = "Unlike base JSON-RPC, the ID MUST NOT be null."
      self.assertRpcError(response, -32600, "Invalid Request", data)

  def test_not_validated_mcp_service(self):
    draft_mcp_service = self.newMCPService("DraftMCPService")
    self.tic()
    conn = MCPClientConnection(self, draft_mcp_service)
    try:
      self._test_request_forbidden(conn)

      draft_mcp_service.validate()
      self.tic()
      response = conn.initialize(protocolVersion=self.protocol_version)
      self.assertEqual(response.getStatus(), 200)

      draft_mcp_service.invalidate()
      self.tic()
      self._test_request_forbidden(conn)
    finally:
      conn.close()

  def _test_request_forbidden(self, conn):
    response = conn.sendMessage(
      "initialize",
      dict(protocolVersion=self.protocol_version),
      JsonRpcType.REQUEST,
    )
    self.assertEqual(response.getStatus(), 403)
    self.assertEqual(response.getBody(), "")

  def test_tools_list_bad_config(self):
    mcp_service = self.newMCPService(
      "MCPServiceWithBadToolList", tool=["Hello World"]
    )
    mcp_service.validate()
    self.tic()
    with self.connection(mcp_service) as conn:
      response = conn.tools_list()
      data = "bad tool configuration line: Hello World"
      self.assertRpcError(response, -32603, "Internal error", data)


class MCPServiceTestCase(ERP5TypeTestCase):
  """Provides ERP5 MCP test fixture and helpers."""

  def afterSetUp(self):
    self.document_to_remove_list = []
    self.tool_list = getattr(self, "tool_list", [])
    self.tool_create_person = self.newTool(**TOOL_CREATE_PERSON)
    self.tool_read_person = self.newTool(**TOOL_READ_PERSON)
    self.mcp_service = self.newMCPService("testMCPService_Service")
    self.mcp_service.validate()
    # XXX Could this permission be automatically set?
    self.mcp_service.manage_permission(
      'Delete objects',
      ["Assignor", "Manager", "Authenticated"],
      acquire=1
    )
    self.tic()

  def beforeTearDown(self):
    for document in self.document_to_remove_list:
      path = document.getRelativeUrl()
      container, _, object_id = path.rpartition('/')
      try:
        parent = self.portal.unrestrictedTraverse(container)
      except KeyError:
        continue
      else:
        if object_id in parent.objectIds():
          parent.manage_delObjects([object_id])
    self.tic()

  def newContent(self, parent, *args, **kwargs):
    document = parent.newContent(*args, **kwargs)
    self.document_to_remove_list.append(document)
    return document

  def newTool(self, *args, **kw):
    """Helper to make new tool- auto creates parameters from list"""
    reference = kw.pop('reference')
    reference_form = "%sForm" % reference
    input_schema = kw.pop('input_schema')
    output_schema = kw.pop('output_schema', None)
    portal_callables = self.portal.portal_callables
    tool_form = self.newContent(
      portal_callables,
      portal_type="JSON Form",
      text_content=input_schema,
      response_schema=output_schema,
      reference=reference_form,
      id=reference_form,
      title=reference_form,
    )
    tool = self.newContent(
      portal_callables,
      *args,
      callable_type="script",
      portal_type="MCP Tool",
      reference=reference,
      **kw
    )
    tool.setSpecificationValue(tool_form)
    self.tool_list.append(tool)
    return tool

  def newMCPService(self, reference, tool=None):
    return self.newContent(
      self.portal.portal_web_services,
      portal_type="MCP Service",
      reference=reference,
      id=reference,
      tool=tool or [
        "List portal type | MCP_listPortalType",
        "List portal types | MCP_listPortalTypes",
        "Get portal type schema | MCP_getPortalTypeSchema",
        "Create a new Person | %s" % self.tool_create_person.getId(),
        "Read persons | %s" % self.tool_read_person.getId(),
      ],
    )

  @contextmanager
  def connection(self, mcp_service=None):
    conn = MCPClientConnection(self, mcp_service)
    try:
      self._initialize(conn)
      yield conn
    finally:
      conn.close()

  def assertToolSuccess(self, result, text_ok):
    self.assertFalse(result["isError"])
    self.assertEqual(result["content"], [{"type": "text", "text": text_ok}])

  def assertToolError(self, result, contains=None, equals=None):
    self.assertTrue(result["isError"])
    text = result["content"][0]["text"]
    if equals is not None:
      self.assertEqual(text, equals)
    if contains:
      for c in contains:
        self.assertIn(c, text)

  def assertRpcError(self, response, code, message, data=None):
    payload = json.loads(response.getBody())
    self.assertIn("error", payload)
    err = payload["error"]
    self.assertEqual(err["code"], code)
    self.assertEqual(err["message"], message)
    if data is not None:
      self.assertEqual(err["data"], data)
    return err

  def assertPersonExists(self, param_dict):
    person_list = self.portal.portal_catalog(
      reference=param_dict['reference'], portal_type="Person"
    )
    self.assertEqual(len(person_list), 1)
    p = person_list[0]
    self.document_to_remove_list.append(p)
    self.assertEqual(p.getFirstName(), param_dict.get("first_name", None))
    self.assertEqual(p.getLastName(), param_dict.get("last_name", None))

  def _initialize(self, conn):
    response = conn.initialize(
      protocolVersion=self.protocol_version,
      capabilities={},
      clientInfo={"version": 1.0, "name": "ERP5 MCP Test Client"}
    )
    result = self._fetchResult(response)
    self.assertEqual(result['protocolVersion'], self.protocol_version)
    session_id = response.getHeader('MCP-Session-Id')
    self.assertIsNotNone(session_id)
    conn.session_id = session_id
    _ = conn.notifications_initialized()
    self.assertEqual(_.getBody(), '')  # notification must return empty response

  def _tools_call(self, conn, name, arguments):
    result = self._fetchResult(conn.tools_call(name=name, arguments=arguments))
    self.tic()
    return result

  def _fetchResult(self, response):
    json_rpc_message = json.loads(response.getBody())
    self.assertIn("result", json_rpc_message)
    return json_rpc_message["result"]


class TestMCPService20250326(MCPServiceTestCase, MCPServiceApiTestMixin):
  protocol_version = "2025-03-26"


class TestMCPService20250618(MCPServiceTestCase, MCPServiceApiTestMixin):
  protocol_version = "2025-06-18"


class TestMCPService20251125(MCPServiceTestCase, MCPServiceApiTestMixin):
  protocol_version = "2025-11-25"


# Test tools for test run
TOOL_CREATE_PERSON = dict(
  id="mcptest_createPerson",
  reference="mcptest_createPerson",
  body=r"""portal = context.getPortalObject()
try:
  person = portal.person_module.newContent(
    portal_type="Person",
    id=reference,
    reference=reference,
    first_name=first_name,
    last_name=last_name,
  )
except Exception as e:
  raise RuntimeError("Could not create person: %s" % e)
person.validate()
return "Succesfully created person %s" % reference""",
  input_schema=r"""{
  "type": "object",
  "properties": {
    "reference": {
      "type": "string"
    },
    "first_name": {
      "type": ["string", "null"]
    },
    "last_name": {
      "type": ["string", "null"]
    }
  },
  "required": ["reference"],
  "additionalProperties": false
}"""
)

TOOL_READ_PERSON = dict(
  id="mcptest_readPerson",
  reference="mcptest_readPerson",
  body=r"""portal = context.getPortalObject()
person_list = portal.portal_catalog(
  portal_type="Person",
  reference=reference
)
text_list = []
data = []
for person in person_list:
  info = dict(
    reference=person.getReference(),
    first_name=person.getFirstName() or "",
    last_name=person.getLastName() or "",
  )
  text_list.append("; ".join(["%s: %s" % (k, info[k]) for k in sorted(info.keys())]))
  data.append(info)
return "\n".join(text_list), {"persons": data}
""",
  input_schema=r"""{
  "type": "object",
  "properties": {
    "reference": {
      "type": "string"
    }
  },
  "required": ["reference"],
  "additionalProperties": false
}""",
  output_schema=r"""{
  "type": "object",
  "properties": {
    "persons": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "reference": {
            "type": "string",
            "description": "A unique identifier for the person"
          },
          "first_name": {
            "type": "string",
            "description": "The person's first name"
          },
          "last_name": {
            "type": "string",
            "description": "The person's last name"
          }
        },
        "required": ["reference", "first_name", "last_name"],
        "additionalProperties": false
      }
    }
  },
  "required": ["persons"],
  "additionalProperties": false
}""",
)


class MCPClientConnection(object):
  def __init__(self, test, mcp_service=None):
    self.test = test
    self.mcp_service = mcp_service or self.test.mcp_service
    self.server_url = self.mcp_service.absolute_url_path()
    erp5_mcp = self.test.portal.portal_skins["erp5_mcp"]
    schema = str(erp5_mcp["MCPSchema%s" % self.test.protocol_version])
    self.schema = json.loads(schema)
    self._callable_map = _buildCallableMap(self.schema)
    self.validator = ProtocolValidator(self.test.portal)
    self.session_id = None

  def __getattr__(self, key):
    if key not in self._callable_map:
      raise AttributeError(key)
    method_name, msg_type = self._callable_map[key]
    is_notification = msg_type == JsonRpcType.NOTIFICATION
    send = self.sendNotification if is_notification else self.sendRequest
    def _(**params):
      return send(method_name, params)
    _.__name__ = key
    setattr(self, key, _)
    return _

  def __del__(self):
    self.close()

  def close(self):
    if self.session_id is None:
      return
    self.mcp_service._getSessionFromId(self.session_id)  # must not raise yet
    response = self.test.publish(
      self.mcp_service.absolute_url_path(),
      request_method="DELETE",
      user="ERP5TypeTestCase",
      env=dict(HTTP_MCP_SESSION_ID=self.session_id),
    )
    self.test.assertEqual(response.getBody(), "")
    self.test.assertEqual(response.getStatus(), 204)
    self.test.assertRaises(
      JsonRpcInvalidRequestError,
      self.mcp_service._getSessionFromId,
      self.session_id
    )
    self.test.assertFalse(self.test.portal.portal_sessions[self.session_id])
    self.session_id = None

  def sendRequest(self, method_name, params):
    response = self.sendMessage(method_name, params, JsonRpcType.REQUEST)
    self.test.assertEqual(response.getStatus(), 200)

    content_type = response.getHeader('content-type')
    self.test.assertEqual(content_type, "application/json")

    data = json.loads(response.getBody())

    request_id = data["id"]
    self.test.assertEqual(request_id, self._request_id)

    try:
      result = data["result"]
    except KeyError:
      self.test.assertIn("error", data)
    else:
      self.validator.validateMCPMessage(
        method_name,
        self.test.protocol_version,
        result,
        JsonRpcType.RESPONSE,
        err=JsonRpcInternalError,
      )

    return response

  def sendNotification(self, *args, **kw):
    kw.setdefault("method_type", JsonRpcType.NOTIFICATION)
    return self.sendMessage(*args, **kw)

  def sendMessage(self, method_name, params, method_type):
    content = self.constructJsonRpcMessage(method_name, params, method_type)
    return self._sendMessage(content, method_type)

  def _sendMessage(self, content, method_type):
    env = {'CONTENT_TYPE': 'application/json'}
    if self.session_id is not None and method_type != JsonRpcType.NOTIFICATION:
      env['HTTP_MCP_SESSION_ID'] = self.session_id
    return self.test.publish(
      self.server_url,
      request_method="POST",
      user="ERP5TypeTestCase",
      stdin=io.BytesIO(json.dumps(content).encode()),
      env=env,
    )

  def constructJsonRpcMessage(self, method_name, params, method_type):
    content = {"jsonrpc": "2.0", "method": method_name}
    if params:
      content["params"] = params
    if method_type == JsonRpcType.REQUEST:
      request_id = getattr(self, "_request_id", 0) + 1
      self._request_id = request_id
      content["id"] = request_id
    return content


def _buildCallableMap(schema):
  mcp_index = _buildMCPIndex(schema)
  callable_map = {}
  for (method_name, msg_type) in mcp_index.keys():
    if msg_type not in (JsonRpcType.REQUEST, JsonRpcType.NOTIFICATION):
      continue
    normalized = method_name.replace("/", "_").replace("-", "_")
    callable_map[normalized] = (method_name, msg_type)
  return callable_map