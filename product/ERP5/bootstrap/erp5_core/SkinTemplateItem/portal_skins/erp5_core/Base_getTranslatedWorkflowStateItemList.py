"""Returns the state item list of a given workflow.
wf_id : the id of workflow. It can be string, list or tuple.

This script is deprecated, it is much recommended to use
ERP5Site_getWorkflowStateItemList by passing the portal type instead.
"""

Base_translateString = context.Base_translateString

if same_type(wf_id, []) or same_type(wf_id, ()):
  workflow_id_list = wf_id
else:
  workflow_id_list = [wf_id]

result = []
for state_title, state_id in context.Base_getWorkflowStateItemList(workflow_id_list=workflow_id_list):
  translated_state_title = Base_translateString(state_title)
  result.append((translated_state_title, state_id))

return result
