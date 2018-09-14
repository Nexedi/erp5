if REQUEST is None:
  REQUEST = context.REQUEST
if response is None:
  response = REQUEST.RESPONSE

default_web_page = context
web_section = REQUEST.get("current_web_section")
#raise ValueError(web_section.getLayoutProperty("configuration_latest_version", default="development"))

mapping_dict={
  "latest_version": web_section.getLayoutProperty("configuration_latest_version", default="development"),
  "latest_document_version": web_section.getLayoutProperty("configuration_latest_document_version", default=context.getWebSiteValue().getId() + "-dev"),
  "redirect_url": web_section.getLayoutProperty("configuration_redirect_url", default=""),
  "cache_file": web_section.getLayoutProperty("configuration_cache_file", default=""),
  "application_name": web_section.getTitle()
}

configuration_webapp_manifest_url = web_section.getLayoutProperty("configuration_webapp_manifest_url", default=None)
if configuration_webapp_manifest_url is None:
  mapping_dict["webapp_manifest_full_link_tag"] = ''
else:
  mapping_dict["webapp_manifest_full_link_tag"] = '<link rel="manifest" href="' + configuration_webapp_manifest_url + '">'


return default_web_page.WebPage_viewAsWeb(mapping_dict=mapping_dict)
