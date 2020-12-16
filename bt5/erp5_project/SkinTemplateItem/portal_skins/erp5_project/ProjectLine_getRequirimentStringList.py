requeriment_list_value = context.getRequirementValueList()
#requeriment_list_title = context.getRequirementTitleList()
requeriment_string_list = []

for req in requeriment_list_value:
  resource_path = '/'.join(req.getPath().split('/')[2:])
  requeriment_string_list.append([req.getTitle(), resource_path ])

return requeriment_string_list
