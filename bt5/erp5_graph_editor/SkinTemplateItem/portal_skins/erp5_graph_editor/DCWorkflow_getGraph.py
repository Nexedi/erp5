import json

# if a graph has been saved, we use this info for node coordinates.
position_graph = context.getProperty('jsplumb_graph')
if position_graph:
  position_graph = json.loads(position_graph)['graph']

# TODO:
#  select after script in edge properties
#  checked box for validation ? or at least select before script

def getDCWorkflowGraph(dc_workflow):
  graph = dict(node=dict(), edge=dict())
  for state in dc_workflow.states.objectValues():
    is_initial_state = state.getId() == dc_workflow.states.initial_state
    graph['node'][state.getId()] = dict(
      _class='dc_workflow.state',
      name=state.title_or_id(),
      is_initial_state="Yes" if is_initial_state else "No")
    if is_initial_state:
      graph['node'][state.getId()]['css'] = { "color": "red" } # TODO: use different CSS for initial state

    for transition in state.transitions:
      if transition in dc_workflow.transitions:
        transition = dc_workflow.transitions[transition]
        if transition.new_state_id:
          graph['edge']["%s_%s" % (state.getId(), transition.id)] = (
              dict(_class='dc_workflow.transition',
                   source=state.getId(),
                   destination=transition.new_state_id,
                   name=transition.actbox_name or transition.title_or_id(),
                   description=transition.description,
                   actbox_url=transition.actbox_url,
                   transition_id=transition.getId() # used for edition.
                  ))

  if position_graph:
    for state_id in graph['node'].keys():
      if state_id in position_graph['node']:
        graph['node'][state_id]['coordinate'] = position_graph['node'][state_id]['coordinate']
  return graph


class_definition = {
  'dc_workflow.transition': {
    '_class': 'edge',
    'type': 'object',
    'description': 'A DCWorkflow Transition',
    'properties': {
      'name': {
        'type': 'string',
        'name': 'Name',
        'description': 'Name of this transition, will be displayed in the document actions',
      },
      'description': {
        'type': 'string',
        'name': 'Description',
      },
      'actbox_url': {
        'type': 'string',
        'name': 'Action URL',
        'description': 'URL of the action, variables will be substitued. XXX TODO: higher level ! just configure "script name" '
      },
    }
  },
  'dc_workflow.state': {
    '_class': 'node',
    'type': 'object',
    'description': 'A DCWorkflow State',
    'properties': {
      'name': {
        'type': 'string',
        'name': 'Name',
        'description': 'The name of the state, will be displayed in document view',
      },
      'id': {
        'type': 'string',
        'name': 'Id',
        'description': 'Id of the state, will be used for catalog searches',
      },
      'is_initial_state': {
        'type': 'string',
        'enum': ['Yes', 'No'],
        'name': 'Is initial State',
        'description': 'Set to Yes if this state is the initial state for newly created documents',
      },
    }
  }
}

return json.dumps(dict(graph=getDCWorkflowGraph(context), class_definition=class_definition), indent=2)
