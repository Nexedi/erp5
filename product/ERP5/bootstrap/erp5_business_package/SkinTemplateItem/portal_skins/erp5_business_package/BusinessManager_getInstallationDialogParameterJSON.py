import json
return json.dumps({
  'item_path_list': context.getParentValue().compareInstallationState([context]),
  'action_url': context.absolute_url() + '/BusinessManager_installFromDialogParameterJSON'
})
