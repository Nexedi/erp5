import json
commit_dict = json.loads(commit_json) if commit_json is not None else {
  'keep': keep
}

if keep:
  commit_dict['keep'] = keep

try:
  new_bt = context.getVcsTool().update(commit_dict['keep'])
except Exception as error:
  return context.BusinessTemplate_handleException(
    error, script.id, commit_dict)

return new_bt.Base_redirect('BusinessTemplate_viewInstallationDialog', keep_items={
  'portal_status_message': 'Working copy updated successfully.',
  'workflow_action': 'install_action',
  'form_id': 'view'
})
