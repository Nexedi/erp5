'''This script is deprecated, it is much recommended to use
ERP5Site_getWorkflowStateItemList by passing the portal type and state_var instead.
'''

from Products.CMFCore.utils import getToolByName

if not (same_type(workflow_id_list, []) or same_type(workflow_id_list, ())):
  workflow_id_list = (workflow_id_list,)

state_dict = {}
item_list = []
for workflow_id in workflow_id_list:
  workflow = getToolByName(context, 'portal_workflow')[workflow_id]
  for state in workflow.getStateValueList():
    state_reference = state.getReference()
    if state.getTitle() and state_reference != 'deleted':
      if state_reference not in state_dict:
        # we hide states without titles
        item_list.append((state.getTitle(), state_reference))
        state_dict[state_reference] = None
return item_list
