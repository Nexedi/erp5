def respond(v):
  if REQUEST is None:
    return v
  REQUEST.RESPONSE.setHeader("Content-Type", "text/html")
  REQUEST.RESPONSE.write(v)
  raise ValueError("Abort Transaction")

return respond(context.Base_formatDiffObjectListToHTML(context.BusinessTemplate_getDiffObjectListFromZODB(detailed=detailed)))
