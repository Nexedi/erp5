import json

if REQUEST is None:
  REQUEST = context.REQUEST
if response is None:
  response = REQUEST.RESPONSE

default_web_page = context
web_section = REQUEST.get("current_web_section")



available_language_set = web_section.getLayoutProperty("available_language_set", default=['en'])
default_language = web_section.getLayoutProperty("default_available_language", default='en')

root_website_url = web_section.getOriginalDocument().absolute_url() + '/'


website_url_set = {}
for tmp in available_language_set:
  if tmp == default_language:
    website_url_set[tmp] = root_website_url
  else:
    website_url_set[tmp] = root_website_url + tmp + '/'


return default_web_page.WebPage_viewAsWeb(mapping_dict={
  "frontpage_gadget": web_section.getLayoutProperty("configuration_frontpage_gadget_url", default="worklist"),
  "application_title": web_section.getLayoutProperty("configuration_application_title", default="ERP5"),
  "action_view": web_section.getLayoutProperty("configuration_view_action_category", default="object_view"),
  "default_view_reference": web_section.getLayoutProperty("configuration_default_view_action_reference", default="view"),
  "hateoas_url": web_section.getLayoutProperty("configuration_hateoas_url", default="hateoas/"),
  "panel_gadget": web_section.getLayoutProperty("configuration_panel_gadget_url", default="gadget_erp5_panel.html"),
  "router_gadget": web_section.getLayoutProperty("configuration_router_gadget_url", default="gadget_erp5_router.html"),
  "header_gadget": web_section.getLayoutProperty("configuration_header_gadget_url", default="gadget_erp5_header.html"),
  "jio_gadget": web_section.getLayoutProperty("configuration_jio_gadget_url", default="gadget_jio.html"),
  "translation_gadget": web_section.getLayoutProperty("configuration_translation_gadget_url", default="gadget_translation.html"),
  "manifest_url": web_section.getLayoutProperty("configuration_manifest_url", default="gadget_erp5.appcache"),
  "language_map": json.dumps({tmp['id']: context.Base_translateString(tmp['title'], lang = tmp['id']) for tmp in context.Localizer.get_languages_map() if tmp['id'] in available_language_set}),
  "website_url_set": json.dumps(website_url_set),
  "selected_language":  context.Localizer.get_selected_language()
})
