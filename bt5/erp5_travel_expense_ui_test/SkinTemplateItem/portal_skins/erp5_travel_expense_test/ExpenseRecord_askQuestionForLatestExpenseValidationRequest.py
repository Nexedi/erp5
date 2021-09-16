expense_validation_request = context.portal_catalog.getResultValue(
  portal_type = 'Expense Validation Request',
  simulation_state = 'validated',
  sort_on = (('creation_date', 'DESC',),))
if expense_validation_request:
  context.getPortalObject().portal_workflow.doActionFor(
    expense_validation_request, 'suspend_action', comment = 'Ask question test')
  return 'ok'

return 'error'
