from zExceptions import Unauthorized
try:
  return context.standard_error_message_template(*args, **kw)
except Unauthorized:
  pass
try:
  return context.getPortalObject().standard_error_message_template(*args, **kw)  # XXX do it with a proxy role ?
except Unauthorized:
  pass
return context.standard_error_message_render(*args, **kw)
