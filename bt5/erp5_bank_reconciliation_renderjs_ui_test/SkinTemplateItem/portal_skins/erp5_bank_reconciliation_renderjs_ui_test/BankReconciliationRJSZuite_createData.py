from DateTime import DateTime

portal = context.getPortalObject()

organisation_portal_type = "Organisation"
organisation_id = "erp5_bank_reconciliation_renderjs_ui_test"
module = portal.getDefaultModule(organisation_portal_type)
organisation = module.newContent(
  portal_type=organisation_portal_type,
  id=organisation_id,
  title=organisation_id
)
bank_account_portal_type = "Bank Account"
bank_account_id = "erp5_bank_reconciliation_bank"
bank_account = organisation.newContent(
  portal_type=bank_account_portal_type,
  id=bank_account_id,
  title=bank_account_id
)

bank_reconciliation_portal_type = "Bank Reconciliation"
bank_reconciliation_id = "erp5_bank_reconciliation_renderjs_ui_test"
module = portal.getDefaultModule(bank_reconciliation_portal_type)
bank_reconciliation = module.newContent(
  portal_type=bank_reconciliation_portal_type,
  id=bank_reconciliation_id,
  title=bank_reconciliation_id,
  source_section_value=organisation,
  source_payment_value=bank_account,
  quantity_range_max=100,
  stop_date=DateTime('2019/10/21')

)
bank_reconciliation.open()

payment_portal_type = "Payment Transaction"
payment_id = "erp5_bank_reconciliation_renderjs_ui_test"
module = portal.getDefaultModule(payment_portal_type)
payment = module.newContent(
  portal_type=payment_portal_type,
  id=payment_id,
  title=payment_id,
  source_section_value=organisation,
  destination_section_value=organisation,
  source_payment_value=bank_account,
  start_date=DateTime('2019/10/20')
)
payment.stop()

return "Bank Reconciliation Created."
