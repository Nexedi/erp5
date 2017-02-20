if REQUEST is None:
  REQUEST = context.REQUEST
if response is None:
  response = REQUEST.RESPONSE

default_web_page = context
web_section = REQUEST.get("current_web_section")

return default_web_page.WebPage_viewAsWeb(mapping_dict={
  "latest_version": web_section.getLayoutProperty("configuration_latest_version", default="development"),
  "latest_document_version": web_section.getLayoutProperty("configuration_latest_document_version", default=context.getWebSiteValue().getId() + "-dev"),
  "redirect_url": web_section.getLayoutProperty("configuration_redirect_url", default=""),
  "cache_file": web_section.getLayoutProperty("configuration_cache_file", default=""),
  "application_name": web_section.getTitle(),
  "sub_gadget_installer": web_section.getLayoutProperty("configuration_sub_gadget_installer", default=""),
})
