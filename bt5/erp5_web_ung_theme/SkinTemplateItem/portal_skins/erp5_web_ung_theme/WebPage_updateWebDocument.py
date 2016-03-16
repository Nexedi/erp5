from json import dumps

catalog_object = context.portal_catalog.getResultValue(path=document_path)
document = context.restrictedTraverse(catalog_object.getPath())

context.setTextContent(document.asStrippedHTML())
context.setTitle(document.getTitle())

if document.getTitle() != context.getTitle() or document.getId() == context.getTitle():
  return dumps(dict(status=400))
 
return dumps(dict(status=200))
