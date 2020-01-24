appcache_reference = context.getLayoutProperty("configuration_manifest_url", default="gadget_erp5.appcache")

web_manifest = context.getPortalObject().portal_catalog.getResultValue(
  portal_type='Web Manifest',
  reference=appcache_reference)

if web_manifest is None:
  text_content = ''
else:
  text_content = web_manifest.getTextContent()

translation_data_url_list = []
url_list = []
for text_line in text_content.split('\n'):
  text_line = text_line.split('/')[-1]
  if text_line.endswith('.html'):
    url_list.append(text_line)
    continue

  if text_line.endswith('.js') and not only_html:
    if text_line.endswith('translation_data.js'):
      translation_data_url_list = [text_line]
      continue
    url_list.append(text_line)
return translation_data_url_list + url_list
