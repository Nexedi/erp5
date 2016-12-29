portal = context.getPortalObject()
state = context.getSimulationState()

if state == "validated":
  return

if (state not in ('accepted')):
  return context.Base_redirect('view',
       keep_items=dict(portal_status_message= portal.Base_translateString("Transaction is not in the right state",),))

context.ExpenseValidationRequest_createPurchaseTransaction()
