# First find the Web Section or Web Site we belong to
search_context = context.getWebSectionValue()

if all_versions is None:
  all_versions = search_context.getLayoutProperty('layout_all_versions', default=False)
if all_languages is None:
  all_languages = search_context.getLayoutProperty('layout_all_languages', default=False)

return context.getPortalObject().portal_catalog.getDocumentValueList(
  search_context=search_context,
  all_versions=all_versions,
  all_languages=all_languages,
  **kw)
