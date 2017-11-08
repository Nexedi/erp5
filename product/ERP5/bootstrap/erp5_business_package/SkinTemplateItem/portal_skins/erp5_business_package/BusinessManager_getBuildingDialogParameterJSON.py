import json

# Get the path list which has been changed/modified in Business Manager
changed_path_list = context.getParentValue().rebuildBusinessManager(context)[1]

return json.dumps({
  'item_path_list': changed_path_list,
})
