# This method outputs the skin properties in the format that you can
# easily get diff like the following:
# ---
# CSV,erp5_access_tab
# CSV,custom
# CSV,erp5_csv_style
# CSV,erp5_csv_core
# ...
# ---
skin_tool = context.getPortalObject().portal_skins
for name, layers in skin_tool.getSkinPaths():
  for layer in layers.split(','):
    if ignore_skin_folder_list is not None and\
        layer in ignore_skin_folder_list:
      continue
    print('%s,%s' % (name, layer))
return printed
