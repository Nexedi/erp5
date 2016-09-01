portal = context.getPortalObject()

date_now = None
if params is not None:
  date_now = params.get('date_now')

for brain in context.portal_catalog(portal_type="Expense Record", simulation_state="draft"):
  if brain.getSimulationState() == 'draft':
    brain.activate().ExpenseRecord_createExpenseValidationItem(date_now=date_now)
