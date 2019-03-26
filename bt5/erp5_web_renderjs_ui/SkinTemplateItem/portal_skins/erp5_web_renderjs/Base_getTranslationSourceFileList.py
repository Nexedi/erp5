import re

service_worker_reference = context.getLayoutProperty("configuration_service_worker_url", default="gadget_erp5_serviceworker.js")

service_worker = context.getPortalObject().portal_catalog.getResultValue(
  portal_type='Web Script',
  reference=service_worker_reference)

if service_worker is None:
  text_content = ''
else:
  text_content = service_worker.getTextContent()

filename_pattern = re.compile("'(?P<filename>[a-zA-Z0-9-_\.\?=]*)'")
filename_list = []

start = False
for line in text_content.split('\n'):
  if start is False and 'REQUIRED_FILES' in line:
    start = True
    continue
  if not line:
    continue
  if start:
    if ']' in line:
      break
    matched = filename_pattern.search(line)
    if matched is not None:
      filename = matched.groupdict().get('filename')
      if filename:
        filename_list.append(filename)

file_list = []
translation_data_file = []
for filename in filename_list:
  if filename.endswith('.html'):
    file_list.append(filename)
    continue

  if filename.endswith('.js') and not only_html:
    if filename.endswith('translation_data.js'):
      translation_data_file = [filename]
      continue
    file_list.append(filename)
return translation_data_file + file_list
