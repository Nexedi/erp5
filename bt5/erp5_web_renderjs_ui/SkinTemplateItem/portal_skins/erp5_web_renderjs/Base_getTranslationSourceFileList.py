filename_list = context.WebSection_getPrecacheManifest()

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
