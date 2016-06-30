from zExceptions import Unauthorized
if REQUEST is not None:
  raise Unauthorized

# XXX requested to simulate in unit test for now
return context.REQUEST.getHeader(name, default)
