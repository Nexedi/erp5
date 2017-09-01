import json

checkNeeded, changed_path_list = context.getParentValue().rebuildBusinessManager(context)

return json.dumps({
  'check_needed': checkNeeded,
  'item_path_list': changed_path_list,
  'action_url': context.absolute_url() + '/BusinessManager_buildFromDialogParameterJSON',
})
