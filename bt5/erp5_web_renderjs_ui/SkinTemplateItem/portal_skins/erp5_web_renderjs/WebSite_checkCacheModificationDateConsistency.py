from DateTime import DateTime
appcache_reference = context.getLayoutProperty("configuration_manifest_url")

error_list = []
if appcache_reference:
  appcache_manifest = context.getDocumentValue(appcache_reference)
  if not appcache_manifest:
    return ['Error: Web Site %s references a non existant appcache %s' % (context.getRelativeUrl(),appcache_reference)]
  url_list = [url for url in context.Base_getListFileFromAppcache() if url]
  # Check that the manifest is newer than all cached resources.
  appcache_manifest_modification_date = appcache_manifest.getObject().getModificationDate()

  if url_list:
    for referenced_document in context.getDocumentValueList(reference=url_list):
      if referenced_document.getModificationDate() > appcache_manifest_modification_date:
        error_list.append(
          "Document {} is newer than cache manifest".format(referenced_document.getReference()))

  if error_list and fixit:
    text_list = appcache_manifest.getTextContent().split('\n')
    assert text_list[0] == 'CACHE MANIFEST', 'First Line of %s should be CACHE MANIFEST' % appcache_manifest.getRelativeUrl()
    appcache_manifest.edit(
        text_content='''{}
# Last modified by {} on {}
{}'''.format(text_list[0], script.getId(), DateTime(), '\n'.join(text_list[1:])))
return error_list
