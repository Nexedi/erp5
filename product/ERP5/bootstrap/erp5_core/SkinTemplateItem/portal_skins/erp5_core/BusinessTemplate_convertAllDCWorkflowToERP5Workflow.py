workflow_tool = context.getPortalObject()
unknown_workflow_id_list = []
for workflow_id in context.getTemplateWorkflowIdList():
  try:
    workflow = workflow_tool[workflow_id]
  except KeyError:
    # In case of bt not already installed or wrong Workflow name
    unknown_workflow_id_list.append(workflow_id)
  else:
    try:
      convert = workflow.convertToERP5Workflow
    except AttributeError:
      # Already converted...
      continue
    else:
      convert()

if unknown_workflow_id_list:
  message = ("Error when converting: %s: Not installed or invalid names?" %
             ', '.join(unknown_workflow_id_list))
  abort_transaction = True
else:
  message = "Conversion of workflows successful."
  abort_transaction = False
return context.Base_redirect(
  'view',
  keep_items=dict(portal_status_message=message),
  abort_transaction=abort_transaction)
