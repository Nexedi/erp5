"""
Fixed plain-text response, used only by the Zelenium test for the
http_request tool (testOfficeJSHarnessAIHttpRequestTool.zpt). Same-origin so
no CORS/proxy is needed, and deterministic so the test doesn't depend on any
real external site staying reachable or unchanged.

With report_cookie=1, it says instead whether the request carried cookies:
http_request must not send the site's cookies of the logged-in user
(testOfficeJSHarnessAIHttpRequestTool.zpt).
"""
request = context.REQUEST
request.RESPONSE.setHeader('Content-Type', 'text/plain')
if request.form.get('report_cookie'):
  return 'Request cookies: %s' % ('yes' if request.getHeader('Cookie') else 'no')
return 'Hello from the fake HTTP endpoint!'
