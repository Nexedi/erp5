from zExceptions import Unauthorized
if REQUEST is not None:
  raise Unauthorized

connector = context.getResourceValue()
connector.processResponse(response, context.getObject(), failed)
