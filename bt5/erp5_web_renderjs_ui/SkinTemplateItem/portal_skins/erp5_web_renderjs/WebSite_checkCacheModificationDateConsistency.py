from DateTime import DateTime

# OfficeJS web sites have been using another layout property (configuration_cache_file)
# to set the cache manifest.
# We support only ERP5JS style cache manifest for now, so if this is an officejs site,
# we ignore cache manifest check.
if context.getLayoutProperty("configuration_cache_file"):
  return []

appcache_reference = context.getLayoutProperty("configuration_manifest_url")

getDocumentValue = context.getDocumentValue

error_list = []
if appcache_reference:
  appcache_manifest = getDocumentValue(appcache_reference)
  if not appcache_manifest:
    return ['Error: Web Site %s references a non existant appcache %s' % (context.getRelativeUrl(),appcache_reference)]
  url_list = context.Base_getListFileFromAppcache()
  # Check that the manifest is newer than all cached resources.
  appcache_manifest_modification_date = appcache_manifest.getObject().getModificationDate()
  for url in url_list:
    if url:
      referenced_document = getDocumentValue(url)
      if referenced_document is not None and (
          referenced_document.getModificationDate() >
          appcache_manifest_modification_date):
        error_list.append(
            "Document {} is newer than cache manifest".format(url))

  if error_list and fixit:
    text_list = appcache_manifest.getTextContent().split('\n')
    assert text_list[0] == 'CACHE MANIFEST', 'First Line of %s should be CACHE MANIFEST' % appcache_manifest.getRelativeUrl()
    appcache_manifest.edit(
        text_content='''{}
# Last modified by {} on {}
{}'''.format(text_list[0], script.getId(), DateTime(), '\n'.join(text_list[1:])))
return error_list
