appcache_reference = context.getLayoutProperty("configuration_manifest_url", default="gadget_erp5.appcache")

web_manifest = context.getPortalObject().portal_catalog.getResultValue(
  portal_type='Web Manifest',
  reference=appcache_reference)

if web_manifest is None:
  text_content = ''
else:
  text_content = web_manifest.getTextContent()

translation_data_file = []
file_list = []
for file in text_content.split('\n'):
  file = file.split('/')[-1]
  if file.endswith('.html'):
    file_list.append(file)
    continue

  if file.endswith('.js') and not only_html:
    if file.endswith('translation_data.js'):
      translation_data_file = [file]
      continue
    file_list.append(file)
return translation_data_file + file_list
