from zExceptions import Unauthorized
if REQUEST is not None:
  raise Unauthorized

origin = context.Base_getRequestHeader("Origin")
if not origin or not (origin.endswith(".app.officejs.com") or origin.endswith(".app.officejs.cn")):
  return

RESPONSE.setHeader("Access-Control-Allow-Credentials", "true")
RESPONSE.setHeader("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")
RESPONSE.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS, HEAD, DELETE, PUT, POST")
RESPONSE.setHeader("Access-Control-Allow-Origin", origin)
RESPONSE.setHeader("Access-Control-Expose-Headers", "Content-Type, Content-Length, WWW-Authenticate, X-Location")
