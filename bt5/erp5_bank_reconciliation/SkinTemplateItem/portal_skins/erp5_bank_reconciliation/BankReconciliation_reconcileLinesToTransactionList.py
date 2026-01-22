portal = context.getPortalObject()

bank_reconciliation_line_uid_list = kw.get("listbox_uid")
accounting_transaction_uid_field_prefix = "field_listbox_aggregate_related_title_"

for bank_reconciliation_line_uid in bank_reconciliation_line_uid_list:
  related_accounting_transaction_uid = kw.get(accounting_transaction_uid_field_prefix + bank_reconciliation_line_uid, None)
  if not related_accounting_transaction_uid:
    continue

  related_accounting_transaction_value = portal.portal_catalog.getObject(related_accounting_transaction_uid)
  related_accounting_transaction_value.setAggregateUid(long(bank_reconciliation_line_uid))

# Since setting aggregate-related can change which lines are simulated, update simulation
context.updateSimulation(expand_root=1)

return context.Base_redirect("view", keep_items={
  "portal_status_message": context.Base_translateString("Lines successfully reconcilied with transactions."),
})
