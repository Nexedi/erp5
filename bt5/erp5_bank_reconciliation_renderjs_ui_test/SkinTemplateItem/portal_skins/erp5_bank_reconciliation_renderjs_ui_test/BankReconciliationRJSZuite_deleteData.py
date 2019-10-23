portal = context.getPortalObject()

bank_reconciliation_portal_type = "Bank Reconciliation"
bank_reconciliation_id = "erp5_bank_reconciliation_renderjs_ui_test"

# Delete bank reconciliation
module = portal.getDefaultModule(bank_reconciliation_portal_type)
if getattr(module, bank_reconciliation_id, None) is not None:
  module.manage_delObjects([bank_reconciliation_id])

payment_portal_type = "Payment Transaction"
payment_id = "erp5_bank_reconciliation_renderjs_ui_test"
# Delete Payment
module = portal.getDefaultModule(payment_portal_type)
if getattr(module, payment_id, None) is not None:
  module.manage_delObjects([payment_id])

organisation_portal_type = "Organisation"
organisation_id = "erp5_bank_reconciliation_renderjs_ui_test"
module = portal.getDefaultModule(organisation_portal_type)
if getattr(module, organisation_id, None) is not None:
  module.manage_delObjects([organisation_id])

return "Deleted Successfully."
