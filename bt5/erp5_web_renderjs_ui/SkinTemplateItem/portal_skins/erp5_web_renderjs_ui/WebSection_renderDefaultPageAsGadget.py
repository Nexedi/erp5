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

view_as_web_method = default_web_page.getTypeBasedMethod(
  "viewAsWeb",
  fallback_script_id="WebPage_viewAsWeb"
  )

mapping_dict = {
  "frontpage_gadget": web_section.getLayoutProperty("configuration_frontpage_gadget_url", default="worklist"),
  "jio_document_page_gadget": web_section.getLayoutProperty("configuration_default_jio_document_page_gadget_url", default="form"),
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
  "stylesheet_url": web_section.getLayoutProperty("configuration_stylesheet_url", default="gadget_erp5_nojqm.css"),
  "service_worker_url": web_section.getLayoutProperty("configuration_service_worker_url", default=""),
  "language_map": json.dumps({tmp['id']: portal.Base_translateString(tmp['title'], lang = tmp['id']) for tmp in portal.Localizer.get_languages_map() if tmp['id'] in available_language_set}),
  "default_selected_language":  portal.Localizer.get_selected_language(),
  "website_url_set": json.dumps(website_url_set),
  "site_description": web_section.getLayoutProperty("description", default=""),
  "site_keywords": web_section.getLayoutProperty("subject", default=""),
}

configuration_manifest_url = web_section.getLayoutProperty("configuration_manifest_url", default=None)
if configuration_manifest_url is None:
  mapping_dict["manifest_attribute"] = ''
else:
  mapping_dict["manifest_attribute"] = 'manifest="%s"' % configuration_manifest_url

configuration_webapp_manifest_url = web_section.getLayoutProperty("configuration_webapp_manifest_url", default=None)
if configuration_webapp_manifest_url is None:
  mapping_dict["webapp_manifest_full_link_tag"] = ''
else:
  mapping_dict["webapp_manifest_full_link_tag"] = '<link rel="manifest" href="' + configuration_webapp_manifest_url + '">'

# base tag
if mapping_dict["default_selected_language"] == default_language:
  mapping_dict["extra_base_tag"] = ""
else:
  mapping_dict["extra_base_tag"] = '<base href="../">'

# Wallpaper
# It can not be done in Javascript, due to CSP protection.
# data- attribute can not be accessed outside the content property
# So, it is easier to insert a data URL for this functionnality
wallpaper_url = web_section.getLayoutProperty("configuration_wallpaper_url", default=None)
if wallpaper_url is None:
  mapping_dict["extra_css_full_link_tag"] = ''
else:
  from base64 import urlsafe_b64encode
  mapping_dict["extra_css_full_link_tag"] = '<link rel="stylesheet" href="data:text/css;base64,%s">' % urlsafe_b64encode("""
  html::after {
    content: "";
    opacity: 0.1;
    top: 0;
    left: 0;
    width : 100%%;
    height: 100%%;
    position: fixed;
    z-index: -1;
    background-size: cover;
    background-position: 0 0;
    background-attachment: fixed;
    background-image: url("%s");
  }
  """ % wallpaper_url)

return view_as_web_method(mapping_dict=mapping_dict)
