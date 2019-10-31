def respond(v):
  if REQUEST is None:
    return v
  REQUEST.RESPONSE.setBody(v, lock=True)
  raise Exception

return respond(context.Base_formatDiffObjectListToText(context.BusinessTemplate_getDiffObjectListFromZODB(detailed=detailed)))
