filename_list = context.WebSection_getPrecacheManifest()

file_list = []
translation_data_file_list = []
for filename in filename_list:
  if filename.endswith('.html'):
    file_list.append(filename)
    continue

  if filename.endswith('.js') and not only_html:
    if filename.endswith('translation_data.js'):
      translation_data_file_list.append(filename)
      continue
    file_list.append(filename)
return sorted(translation_data_file_list) + sorted(file_list)
