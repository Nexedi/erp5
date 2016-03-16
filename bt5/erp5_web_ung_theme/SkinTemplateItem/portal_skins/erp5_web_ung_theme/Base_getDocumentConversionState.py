from json import dumps

catalog_object = context.portal_catalog.getResultValue(path=path)

if catalog_object is None:
 print dumps("empty")
 return printed

document = context.restrictedTraverse(catalog_object.getPath())

print dumps(document.getExternalProcessingState())
return printed
