from zExceptions import Unauthorized
if REQUEST is not None:
  raise Unauthorized

RESPONSE.setHeader("Access-Control-Allow-Credentials", "true")
RESPONSE.setHeader("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")
RESPONSE.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS, HEAD, DELETE, PUT, POST")
RESPONSE.setHeader("Access-Control-Allow-Origin", context.Base_getRequestHeader("Origin"))
RESPONSE.setHeader("Access-Control-Expose-Headers", "Content-Type, Content-Length, WWW-Authenticate, X-Location")
