from DateTime import DateTime
appcache_reference = context.getLayoutProperty("configuration_manifest_url")

getDocumentValue = context.getDocumentValue

error_list = []
if appcache_reference:
  url_list = context.Base_getListFileFromAppcache()
  # Check that the manifest is newer than all cached resources.
  appcache_manifest = getDocumentValue(appcache_reference)
  if appcache_manifest is not None:
    appcache_manifest = appcache_manifest.getObject()
    appcache_manifest_modification_date = appcache_manifest.getModificationDate()
  for url in url_list:
    if url:
      referenced_document = getDocumentValue(url)
      if referenced_document is not None and (
          referenced_document.getModificationDate() >
          appcache_manifest_modification_date):
        error_list.append(
            "Document {} is newer than cache manifest".format(url))

  if error_list and fixit:
    appcache_manifest.edit(
        text_content='''# Last modified by {} on {}
{}
'''.format(script.getId(), DateTime(), appcache_manifest.getTextContent()))

return error_list
