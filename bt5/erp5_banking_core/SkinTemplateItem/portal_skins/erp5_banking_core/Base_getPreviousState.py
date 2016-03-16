# Get the id of the user which last passed given transition on given workflow.
workflow_item_list = context.Base_getWorkflowHistoryItemList(workflow_id, display=0)
workflow_item_list.reverse()
previous_state = None
found_given_state = 0
for workflow_item in workflow_item_list:
  current_state = workflow_item.getProperty('state')
  if current_state == state:
    found_given_state = 1
    continue
  if found_given_state and (current_state != state):
    previous_state = current_state
    break
return previous_state
