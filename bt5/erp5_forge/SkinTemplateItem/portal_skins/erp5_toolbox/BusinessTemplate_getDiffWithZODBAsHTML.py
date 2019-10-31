def respond(v):
  if REQUEST is None:
    return v
  REQUEST.RESPONSE.setHeader("Content-Type", "text/html")
  REQUEST.RESPONSE.setBody(v, lock=True)
  raise Exception

return respond(context.Base_formatDiffObjectListToHTML(context.BusinessTemplate_getDiffObjectListFromZODB(detailed=detailed)))
