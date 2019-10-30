from transaction import doom
from zExceptions import Success

def respond(v):
  if REQUEST is None:
    return v
  doom()
  raise Success(v)

return respond(context.Base_formatDiffObjectListToText(context.BusinessTemplate_getDiffObjectListFromZODB(detailed=detailed)))
