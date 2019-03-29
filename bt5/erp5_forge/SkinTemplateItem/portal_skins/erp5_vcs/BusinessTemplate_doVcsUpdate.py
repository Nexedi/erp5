try:
  new_bt = context.getVcsTool().update(keep)
except Exception as error:
  return context.BusinessTemplate_handleException(
    error, script.id, form_id=form_id, keep=keep)

request = context.REQUEST
request.set('portal_status_message', 'Working copy updated successfully.')
return request.RESPONSE.redirect(
  '%s/BusinessTemplate_viewInstallationDialog?workflow_action=install_action&form_id=%s'
  % (new_bt.absolute_url_path(), form_id))
