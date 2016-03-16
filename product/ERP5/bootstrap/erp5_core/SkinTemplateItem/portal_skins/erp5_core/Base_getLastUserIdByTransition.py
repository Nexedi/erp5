# Get the id of the user which last passed given transition on given workflow.
workflow_item_list = context.Base_getWorkflowHistoryItemList(workflow_id, display=0)
workflow_item_list.reverse()
for workflow_item in workflow_item_list:
  if workflow_item.getProperty('action') == transition_id:
    return workflow_item.getProperty('actor')
return None
