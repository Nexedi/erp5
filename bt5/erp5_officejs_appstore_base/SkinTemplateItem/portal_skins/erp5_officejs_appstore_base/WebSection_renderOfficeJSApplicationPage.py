if REQUEST is None:
  REQUEST = context.REQUEST
if response is None:
  response = REQUEST.RESPONSE

default_web_page = context
web_section = REQUEST.get("current_web_section")
#raise ValueError(web_section.getLayoutProperty("configuration_latest_version", default="development"))

return default_web_page.WebPage_viewAsWeb(mapping_dict={
  "latest_version": web_section.getLayoutProperty("configuration_latest_version", default="development"),
  #"application_appcache": web_section.getId() + ".appcache",
})
