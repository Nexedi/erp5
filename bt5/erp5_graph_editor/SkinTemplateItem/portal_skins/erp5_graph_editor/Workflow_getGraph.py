import json
from Products.ERP5Type.Utils import getTranslationStringWithContext

# TODO:
#  select after script in edge properties
#  checked box for validation ? or at least select before script

def getWorkflowGraph(workflow):
  workflow_id = workflow.getId()
  graph = {'node': {}, 'edge': {}}
  for state in workflow.getStateValueList():
    is_initial_state = state.getId() == workflow.getSourceId()
    transition_list = []
    state_name = state.getId()
    state_title = state.getTitle()
    if state_title:
      translated_state_title = getTranslationStringWithContext(context, state_title, 'state', workflow_id)
      if translated_state_title:
        state_name = translated_state_title
    graph['node'][state.getId()] = {
      '_class':'workflow.state',
      'name': state_name,
      'is_initial_state': is_initial_state,
      'path': state.getPath()
    }

    for transition in state.getDestinationValueList():
      transition_id = transition.getReference()
      if transition_id in workflow.getTransitionReferenceList():
        if transition.getDestinationId():
          transition_name = transition.getActionName() or transition.getTitleOrId()
          translated_transition_name = getTranslationStringWithContext(context, transition_name, 'transition', workflow_id)
          if translated_transition_name:
            transition_name = translated_transition_name
          graph['edge']["%s_%s" % (state.getId(), transition.getId())] = ({
            '_class': 'workflow.transition',
            'source': state.getId(),
            'destination': transition.getDestinationId(),
            'name': transition_name,
            'description': transition.getDescription(),
            'actbox_url': transition.getAction(),
            'transition_id': transition.getId(), # used for edition.
            'path': transition.getPath()
          })

    if transition_list:
      graph['edge']['transition_to_%s' % (state.getId())] = {
        '_class':'workflow.transition',
        'source':state.getId(),
        'destination': state.getId(),
        'name_path_dict': {transition.getTitleOrId(): transition.getPath() for transition in transition_list}
      }


  position_graph = context.getProperty('jsplumb_graph')
  if position_graph:
    # if a graph has been saved, we use this info for node coordinates.
    position_graph = json.loads(position_graph)['graph']
  else:
    position_graph = context.ERP5Site_getGraphEditorGraphLayout(graph)

  for state_id in graph['node']:
    if state_id in position_graph['node']:
      graph['node'][state_id]['coordinate'] = position_graph['node'][state_id]['coordinate']
  return graph

return json.dumps(
  dict(graph=getWorkflowGraph(context), class_definition={}),
  sort_keys=True,
  indent=2)
