# Returns a list of tuples (region, Folder) representing amortisation methods,
# deducted from available methods
return_list = []

# Find the accounting regions
skin_dir_list = context.portal_skins.objectValues()
for skin_dir in skin_dir_list:
  id = skin_dir.getId()
  id_tokens = id.split('_')
  if len(id_tokens) == 3 and id_tokens[:2] == ['erp5','accounting']:
    region = id_tokens[2]
    # Determine amortisation methods available in this region
    for subfolder in skin_dir.objectValues():
      if "ratioCalculation" in [o.getId() for o in subfolder.objectValues()]:
        return_list.append((region,subfolder))

return return_list
