'''Returns a list of items (state_title, state_id) of the workflows that are chained
to the given portal_type(s). This can also be filtered to workflows that are using
a given state_var (simulation_state, validation_state etc).

display_none_category argument controls wether the list will contain an empty item 
as first element or not (just like category tool API)

The state titles will be translated unless you pass translate=False
'''
from six import string_types as basestring
if translate:
  from Products.ERP5Type.Message import translateString
else:
  translateString = lambda msg: msg

portal = context.getPortalObject()
workflow_tool = portal.portal_workflow
workflow_set = set() # existing workflows.
state_set = set(['deleted']) # existing state ids (we do not want to return a same state id twice 
                             # if more than one workflow define the same state). Also note that we
                             # always ignore deleted state.

result_list = display_none_category and [('', '')] or []

if isinstance(portal_type, basestring):
  portal_type = portal_type,
  
type_tool = portal.portal_types
for portal_type in portal_type:
  portal_type = getattr(type_tool, portal_type)
  for workflow_id in portal_type.getTypeWorkflowList():
    if workflow_id in workflow_set:
      continue
    workflow_set.add(workflow_id)
    
    workflow = workflow_tool[workflow_id]
    
    state_value_list = workflow.getStateValueList()
    # skip interaction workflows or workflows with only one state (such as edit_workflow)
    if len(state_value_list) <= 1:
      continue
    
    # skip workflows using another state variable
    if state_var not in (None, workflow.getStateVariable()):
      continue
    
    for state in state_value_list:
      state_reference = state.getReference()
      if state_reference in state_set:
        continue
      state_set.add(state_reference)
      
      result_list.append((str(translateString(state.getTitle())), state_reference))

return result_list
