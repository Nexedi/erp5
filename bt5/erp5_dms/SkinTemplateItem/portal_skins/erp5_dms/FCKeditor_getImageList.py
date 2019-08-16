result = context.FCKeditor_getDocumentListQuery(document_type='Image')
if result is not None:
  kw['query'] = result
return context.getPortalObject().portal_catalog(**kw)
