"""
Fake MCP server (Streamable HTTP transport, JSON-RPC 2.0 over POST), used only
by the Zelenium test for the MCP client of officejs_harness_ai
(testOfficeJSHarnessAIMcpServer.zpt, gadget_officejs_harness_ai_mcp_client_js.js).
Same-origin, so the app's Content-Security-Policy connect-src already allows it.

Stateless: the session id is a fixed value, checked on every request after
initialize, so the test sees the client sends back the Mcp-Session-Id header.

- initialize                 -> server info, with the Mcp-Session-Id header
- notifications/initialized  -> 202, empty body
- tools/list                 -> two pages (nextCursor), one tool on each, so
                                 the client must follow the cursor:
                                 echo (page 1) and fail (page 2)
- tools/call echo            -> answered as an SSE stream (text/event-stream),
                                 "MCP-ECHO: <text> (session <session id>)"
- tools/call fail            -> a result with isError, "FAKE-MCP-FAILURE"
"""
import json

SESSION_ID = 'fake-mcp-session'
PROTOCOL_VERSION = '2025-06-18'

request = context.REQUEST
response = request.RESPONSE
message = json.loads(request.get('BODY', '') or '{}')
method = message.get('method')
params = message.get('params') or {}


def reply(result):
  response.setHeader('Content-Type', 'application/json')
  return json.dumps({'jsonrpc': '2.0', 'id': message.get('id'), 'result': result})


if method == 'initialize':
  response.setHeader('Mcp-Session-Id', SESSION_ID)
  return reply({
      'protocolVersion': PROTOCOL_VERSION,
      'capabilities': {'tools': {}},
      'serverInfo': {'name': 'fake-mcp-server', 'version': '1.0'},
  })

session_id = request.getHeader('Mcp-Session-Id')
if session_id != SESSION_ID:
  # Like a real server, a request without the session of initialize is
  # rejected: the client then sees "HTTP 400".
  response.setStatus(400)
  response.setHeader('Content-Type', 'text/plain')
  return 'Missing or unknown Mcp-Session-Id: %s' % session_id

if method == 'notifications/initialized':
  response.setStatus(202)
  return ''

if method == 'tools/list':
  if params.get('cursor') == 'page-2':
    return reply({'tools': [{
        'name': 'fail',
        'description': 'FAKE-MCP-FAIL tool: always reports an error.',
        'inputSchema': {'type': 'object', 'properties': {}},
    }]})
  return reply({
      'tools': [{
          'name': 'echo',
          'description': 'FAKE-MCP-ECHO tool: returns the given text.',
          'inputSchema': {
              'type': 'object',
              'properties': {'text': {'type': 'string'}},
              'required': ['text'],
          },
      }],
      'nextCursor': 'page-2',
  })

if method == 'tools/call' and params.get('name') == 'echo':
  response.setHeader('Content-Type', 'text/event-stream')
  return 'event: message\ndata: %s\n\n' % json.dumps({
      'jsonrpc': '2.0',
      'id': message.get('id'),
      'result': {'content': [{
          'type': 'text',
          'text': 'MCP-ECHO: %s (session %s)' % (
              (params.get('arguments') or {}).get('text'), session_id),
      }]},
  })

if method == 'tools/call' and params.get('name') == 'fail':
  return reply({'content': [{'type': 'text', 'text': 'FAKE-MCP-FAILURE'}], 'isError': True})

response.setHeader('Content-Type', 'application/json')
return json.dumps({'jsonrpc': '2.0', 'id': message.get('id'),
                   'error': {'code': -32601, 'message': 'Method not found: %s' % method}})
