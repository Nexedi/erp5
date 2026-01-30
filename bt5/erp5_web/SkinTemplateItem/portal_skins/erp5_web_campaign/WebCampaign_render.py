reference = context.WebCampaign_getDefaultPageReference()
document_list = context.portal_catalog.getDocumentValueList(
  reference=reference,
  limit=1
)
if document_list:
  document = document_list[0]
  render_method_id = context.getProperty('render_method_id', None)
  if render_method_id:
    return getattr(document, render_method_id)()
  else:
    return document.WebPage_viewAsEmbeddedWeb()
