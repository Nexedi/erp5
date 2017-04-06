import json
import re

if REQUEST is None:
  REQUEST = context.REQUEST
if response is None:
  response = REQUEST.RESPONSE

default_web_page = context
web_section = REQUEST.get("current_web_section")

available_language_set = web_section.getLayoutProperty("available_language_set", default=['en'])
portal = context.getPortalObject()
default_language = web_section.getLayoutProperty("default_available_language", default='en')
website_url_set = {}

#simplify code of Base_doLanguage, can't ues Base_doLanguage directly
root_website_url = web_section.getOriginalDocument().absolute_url()
website_url_pattern = r'^%s(?:%s)*(/|$)' % (
  re.escape(root_website_url),
  '|'.join('/' + re.escape(x) for x in available_language_set))

for language in available_language_set:
  if language == default_language:
    website_url_set[language] = re.sub(website_url_pattern, r'%s/\1' % root_website_url, web_section.absolute_url())
  else:
    website_url_set[language]=  re.sub(website_url_pattern, r'%s/%s/\1' % (root_website_url, language), web_section.absolute_url())

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
  "language_map": json.dumps({tmp['id']: portal.Base_translateString(tmp['title'], lang = tmp['id']) for tmp in portal.Localizer.get_languages_map() if tmp['id'] in available_language_set}),
  "default_selected_language":  portal.Localizer.get_selected_language(),
  "website_url_set": json.dumps(website_url_set),
  "site_description": web_section.getLayoutProperty("description", default=""),
  "site_keywords": web_section.getLayoutProperty("subject", default=""),
})
