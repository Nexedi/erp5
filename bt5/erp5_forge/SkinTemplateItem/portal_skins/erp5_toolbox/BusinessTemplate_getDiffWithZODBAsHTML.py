from transaction import doom
from zExceptions import Success

def respond(v):
  if REQUEST is None:
    return v
  REQUEST.RESPONSE.setHeader("Content-Type", "text/html")
  doom()
  raise Success(v)

return respond(context.Base_formatDiffObjectListToHTML(context.BusinessTemplate_getDiffObjectListFromZODB(detailed=detailed)))
