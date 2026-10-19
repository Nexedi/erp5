"""
Fixed plain-text response, used only by the Zelenium test for the
http_request tool (testOfficeJSHarnessAIHttpRequestTool.zpt). Same-origin so
no CORS/proxy is needed, and deterministic so the test doesn't depend on any
real external site staying reachable or unchanged.
"""
request = context.REQUEST
request.RESPONSE.setHeader('Content-Type', 'text/plain')
return 'Hello from the fake HTTP endpoint!'
