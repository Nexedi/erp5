"""Sets up an Workflow with defaults variables needed by ERP5.
"""
for state_id, state_title in (('draft', 'Draft'),):
  state = context.newContent(portal_type='State')
  state.setReference(state_id)
  state.setTitle(state_title)
context.setSourceValue(state)
for v, property_dict in (
      ('action', {
          'description': 'Transition id',
          'variable_expression': 'transition/getReference|nothing',
          'for_status': 1,
          'automatic_update': 1,
        }),
      ('actor', {
          'description': 'Name of the user who performed transition',
          'variable_expression': 'user/getIdOrUserName',
          'for_status': 1,
          'automatic_update': 1,
        }),
      ('comment', {
          'description': 'Comment about transition',
          'variable_expression': "python:state_change.kwargs.get('comment', '')",
          'for_status': 1,
          'automatic_update': 1,
        }),
      ('history', {
          'description': 'Provides access to workflow history',
          'variable_expression': 'state_change/getHistory',
        }),
      ('time', {
          'description': 'Transition timestamp',
          'variable_expression': 'state_change/getDateTime',
          'for_status': 1,
          'automatic_update': 1,
        }),
      ('error_message', {
          'description': 'Error message if validation failed',
          'for_status': 1,
          'automatic_update': 1,
        }),
      ('portal_type', {
          'description': 'Portal type (used as filter for worklists)',
          'for_catalog': 1,
        }),
    ):
  variable = context.newContent(portal_type='Workflow Variable')
  variable.setReference(v)
  variable.edit(**property_dict)
context.setStateVariable('simulation_state')
