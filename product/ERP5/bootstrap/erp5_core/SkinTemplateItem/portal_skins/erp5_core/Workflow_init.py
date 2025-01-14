"""
Set up an Workflow with defaults variables needed by ERP5
"""
state = context.newContent(portal_type='Workflow State', reference='draft', title='Draft')
context.setSourceValue(state)
context.setManagerBypass(True)

for v, property_dict in (
      ('action', {
          'description': 'Transition id',
          'variable_default_expression': 'transition/getReference|nothing',
          'for_catalog': 0,
          'automatic_update': 1,
        }),
      ('actor', {
          'description': 'Name of the user who performed transition',
          'variable_default_expression': 'user/getIdOrUserName',
          'for_catalog': 0,
          'automatic_update': 1,
        }),
      ('comment', {
          'description': 'Comment about transition',
          'variable_default_expression': "python:state_change.kwargs.get('comment', '')",
          'for_catalog': 0,
          'automatic_update': 1,
        }),
      ('history', {
          'description': 'Provides access to workflow history',
          'for_catalog': 0,
          'status_included': 0,
          'automatic_update': 0,
          'variable_default_expression': 'state_change/getHistory',
        }),
      ('time', {
          'description': 'Transition timestamp',
          'variable_default_expression': 'state_change/getDateTime',
          'for_catalog': 0,
          'automatic_update': 1,
        }),
      ('error_message', {
          'description': 'Error message if validation failed',
          'for_catalog': 0,
          'automatic_update': 1,
        }),
      ('portal_type', {
          'description': 'Portal type (used as filter for worklists)',
          'for_catalog': 1,
          'status_included': 0,
          'automatic_update': 0,
        }),
    ):
  variable = context.newContent(portal_type='Workflow Variable')
  variable.setReference(v)
  variable.edit(**property_dict)
