'''Returns a list of items (state_title, state_id) of the workflows that are chained
to the given portal_type(s). This can also be filtered to workflows that are using
a given state_var (simulation_state, validation_state etc).

display_none_category argument controls wether the list will contain an empty item 
as first element or not (just like category tool API)

The state titles will be translated unless you pass translate=False
'''
if translate:
  from Products.ERP5Type.Message import translateString
else:
  translateString = lambda msg: msg

workflow_tool = context.getPortalObject().portal_workflow
workflow_set = set() # existing workflows.
state_set = set(['deleted']) # existing state ids (we do not want to return a same state id twice 
                             # if more than one workflow define the same state). Also note that we
                             # always ignore deleted state.

result_list = display_none_category and [('', '')] or []

if isinstance(portal_type, basestring):
  portal_type = portal_type,

portal = context.getPortalObject()
if isinstance(portal_type, str):
  portal_type = (portal_type,)
for current_type in portal_type:
  current_type = getattr(portal.portal_types, current_type)
  current_workflow_list = current_type.getTypeWorkflowList()
  for workflow_id in current_workflow_list:
    if workflow_id not in workflow_set:
      workflow_set.add(workflow_id)
      workflow = workflow_tool[workflow_id]
      state_value_list = workflow.getStateValueList()
      if (state_value_list is not None and
          len(workflow.getStateIdList()) > 1 and
          state_var in (None, workflow.getStateVariable())):
        for state in state_value_list:
          state_id = state.getReference()
          if not state_id in state_set:
            state_set.add(state_id)
            result_list.append((str(translateString(state.title)), state_id))

return result_list
