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
  
chain_dict = workflow_tool.getWorkflowChainDict()
for portal_type in portal_type:
  for workflow_id in chain_dict['chain_%s' % portal_type].split(','):
    workflow_id = workflow_id.strip()
    if workflow_id in workflow_set:
      continue
    workflow_set.add(workflow_id)
    
    workflow = workflow_tool[workflow_id]
    
    # skip interaction workflows or workflows with only one state (such as edit_workflow)
    if workflow.states is None or len(workflow.states.objectIds()) <= 1:
      continue
    
    # skip workflows using another state variable
    if state_var not in (None, workflow.variables.getStateVar()):
      continue
    
    for state in workflow.states.objectValues():
      if state.id in state_set:
        continue
      state_set.add(state.id)
      
      result_list.append((str(translateString(state.title)), state.id))

return result_list
