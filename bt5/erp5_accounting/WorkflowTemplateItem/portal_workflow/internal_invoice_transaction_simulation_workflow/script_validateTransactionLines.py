from Products.ERP5Type.Core.Workflow import ValidationFailed
from Products.ERP5Type.Message import translateString

internal_invoice = state_change['object']
old_state = state_change['old_state']
if old_state.getId() == 'draft':
  if internal_invoice.InternalInvoiceTransaction_getAuthenticatedUserSection() == internal_invoice.getDestinationSection():
    raise ValidationFailed(translateString("Your entity should not be destination."))

return state_change.getPortal().portal_workflow.accounting_workflow[script.getId()](state_change)
