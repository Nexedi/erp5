def respond(v):
  if REQUEST is None:
    return v
  REQUEST.RESPONSE.write(v)
  raise ValueError("Abort Transaction")

return respond(context.Base_formatDiffObjectListToText(context.BusinessTemplate_getDiffObjectListFromZODB(detailed=detailed)))
