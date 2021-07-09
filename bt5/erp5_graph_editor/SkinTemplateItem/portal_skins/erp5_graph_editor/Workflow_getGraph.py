import json

# if a graph has been saved, we use this info for node coordinates.
position_graph = context.getProperty('jsplumb_graph')
if position_graph:
  position_graph = json.loads(position_graph)['graph']

# TODO:
#  select after script in edge properties
#  checked box for validation ? or at least select before script

def getWorkflowGraph(workflow):
  graph = {'node': {}, 'edge': {}}
  for state in workflow.getStateValueList():
    is_initial_state = state.getId() == workflow.getSourceId()
    transition_list = []
    graph['node'][state.getId()] = {
      '_class':'workflow.state',
      'name': state.getTitleOrId(),
      'is_initial_state': is_initial_state,
      'path': state.getPath()
    }

    for transition in state.getDestinationValueList():
      transition_id = transition.getReference()
      if transition_id in workflow.getTransitionReferenceList():
        if transition.getDestinationId():
          graph['edge']["%s_%s" % (state.getId(), transition.getId())] = ({
            '_class': 'workflow.transition',
            'source': state.getId(),
            'destination': transition.getDestinationId(),
            'name': transition.getActionName() or transition.getTitleOrId(),
            'description': transition.getDescription(),
            'actbox_url': transition.getAction(),
            'transition_id': transition.getId(), # used for edition.
            'path': transition.getPath()
          })
        else:
          # user action
          transition_list.append(transition)

    if transition_list != []:
      graph['edge']['transition_to_%s' % (state.getId())] = {
        '_class':'workflow.transition',
        'source':state.getId(),
        'destination': state.getId(),
        'name_path_dict': {transition.getTitleOrId(): transition.getPath() for transition in transition_list}
      }


  if position_graph:
    for state_id in graph['node'].keys():
      if state_id in position_graph['node']:
        graph['node'][state_id]['coordinate'] = position_graph['node'][state_id]['coordinate']
  return graph

return json.dumps(dict(graph=getWorkflowGraph(context), class_definition={}), indent=2)
