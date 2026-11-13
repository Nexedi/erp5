"""
Stand-in for pygolang-proxy, used only by testOfficeJSHarnessAIProxyServer.zpt
with the "Proxy Server URL" (External service) pointed at this script: the
client then POSTs every outgoing call to "<this script>/proxy" with the real
target in X-Target-URL (and X-Target-Method / X-Target-Headers).

It does not reach the network, it only serves the targets the tests use:
- .../ERP5Site_fakeChatCompletions/<subpath> -> answered by that script, with
  the same request body, so the LLM calls and the Setting's model list keep
  working through the proxy
- .../ERP5Site_fakeHttpEndpoint...           -> answered by that script; with
  "fake_proxy_redirect" in the URL, X-Final-URL reports another URL, like a
  redirect followed by the real proxy
- a host ending in ".invalid"                 -> the proxy's own DNS error:
  status 502, X-Proxy-Error: 1, {"error": "cannot resolve ..."}
"""
import json

request = context.REQUEST
response = request.RESPONSE
portal_url = context.getPortalObject().absolute_url()

if traverse_subpath != ['proxy']:
  response.setStatus(404)
  return 'only POST /proxy is accepted'

target = request.getHeader('X-Target-URL') or ''
host = target.split('://', 1)[-1].split('/', 1)[0]

if '/ERP5Site_fakeChatCompletions' in target:
  subpath = target.split('/ERP5Site_fakeChatCompletions', 1)[1].split('?', 1)[0]
  request.set('traverse_subpath', [name for name in subpath.split('/') if name])
  return context.ERP5Site_fakeChatCompletions()

if '/ERP5Site_fakeHttpEndpoint' in target:
  if 'fake_proxy_redirect' in target:
    response.setHeader('X-Final-URL', portal_url + '/ERP5Site_fakeHttpEndpoint?redirected_by=fake_proxy')
  else:
    response.setHeader('X-Final-URL', target)
  return context.ERP5Site_fakeHttpEndpoint()

response.setStatus(502)
response.setHeader('Content-Type', 'application/json')
response.setHeader('X-Proxy-Error', '1')
if host.endswith('.invalid'):
  return json.dumps({'error': 'cannot resolve %s: [Errno -2] Name or service not known' % host})
return json.dumps({'error': 'upstream failure: the fake proxy does not serve %s' % target})
