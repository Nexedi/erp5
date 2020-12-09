try:
  new_bt = context.getVcsTool().update(keep)
except Exception, error:
  return context.BusinessTemplate_handleException(
    error, script.id, form_id=form_id, keep=keep)

return new_bt.Base_redirect('BusinessTemplate_viewInstallationDialog', keep_items={
  'portal_status_message': 'Working copy updated successfully.',
  'workflow_action': 'install_action',
  'form_id': form_id
})
