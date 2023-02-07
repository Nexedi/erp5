reference = context.WebCampaign_getDefaultPageReference()
render_method_id = context.getProperty('render_method_id', None)

document =context.WebSection_getDocumentValue(reference)

if render_method_id and document:
  result = getattr(document, render_method_id)()
  return result

elif document:
  return document.EmbeddedWebPage_viewAsWeb()
