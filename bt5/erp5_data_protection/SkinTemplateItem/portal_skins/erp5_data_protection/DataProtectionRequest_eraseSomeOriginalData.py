portal = context.getPortalObject()
selection_name = 'data_protection_request_erase_data_selection'
property_id_list = portal.portal_selections.getSelectionCheckedUidsFor(selection_name)
# clean up selection
portal.portal_selections.setSelectionCheckedUidsFor(selection_name, ())
document_to_cleanup = context.getAgentValue()
clean_up_done = False

# First: Purge workflow history comments
if flush_worklfow_history_comment:
  document_to_cleanup.Base_purgeWorkflowHistoryCommentList()
  edit_message = portal.Base_translateString('Workflow comments deleted by data protection manager')
  portal.portal_workflow.doActionFor(document_to_cleanup, 'edit_action', comment=edit_message)
  clean_up_done = True

# Second: erase properties
if property_id_list:
  edit_kw = {}
  [edit_kw.update({property_id: None}) for property_id in property_id_list]

  edit_message = portal.Base_translateString('Properties deleted by data protection manager: ${items}',
                                             mapping={'items': ', '.join(property_id_list)})
  portal.portal_workflow.doActionFor(document_to_cleanup, 'edit_action', comment=edit_message)
  document_to_cleanup.edit(**edit_kw)
  clean_up_done = True

if clean_up_done:
  msg = portal.Base_translateString('Data erased.')
  # Then remove 'View History' permission to everyone except manager
  document_to_cleanup.manage_permission('View History', ['Manager'], 0)
else:
  msg = portal.Base_translateString('No change occurs.')

return context.Base_redirect(form_id, keep_items={'portal_status_message': msg}, **kw)
