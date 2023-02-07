reference_list = context.WebCampaign_getRelatedDocumentReferenceList(aggregate=True)
render_method_id = context.getProperty('render_method_id', None)

document =context.WebSection_getDocumentValue(name=reference_list)

if render_method_id and document:
  result = getattr(document, render_method_id)()
  return result

elif document:
  return document.EmbeddedWebPage_viewAsWeb()
