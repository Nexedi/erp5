from DateTime import DateTime
portal = context.getPortalObject()
appcache_reference = context.getLayoutProperty("configuration_manifest_url")

getDocumentValue = context.getDocumentValue

error_list = []
if appcache_reference:
  url_list = context.Base_getListFileFromAppcache()
  # Check that the manifest is newer than all cached resources.
  appcache_manifest = getDocumentValue(appcache_reference).getObject()
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

# Check that the web page is more recent that the default pages.
if context.getAggregate():
  max_content_modification_date = context.getModificationDate()
  for default_page_reference in context.getAggregateReferenceList():
    if default_page_reference:
      default_page = getDocumentValue(default_page_reference)
      if default_page is not None:
        max_content_modification_date = max(
            default_page.getModificationDate(), max_content_modification_date)
  if context.getModificationDate() < max_content_modification_date:
    error_list.append("Web Site is older than default page")
    if fixit:
      portal.portal_workflow.doActionFor(
          context,
          'edit_action',
          comment='Edit Web Site, it was older than default page')

return error_list
