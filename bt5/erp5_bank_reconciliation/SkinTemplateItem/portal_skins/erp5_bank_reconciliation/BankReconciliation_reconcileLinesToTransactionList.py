portal = context.getPortalObject()
translateString = context.Base_translateString

for line in listbox:
  related_accounting_transaction_uid = line.get("aggregate_related_title", None)
  if not related_accounting_transaction_uid:
    continue

  related_accounting_transaction_value = portal.portal_catalog.getObject(related_accounting_transaction_uid)
  related_accounting_transaction_value.AccountingTransactionLine_addBankReconciliation(
    bank_reconciliation_relative_url=line["listbox_key"],
    message=translateString("Reconciling Bank Line"),
  )

# Since setting aggregate-related can change which lines are simulated, update simulation
context.updateSimulation(expand_root=1)

return context.Base_redirect("view", keep_items={
  "portal_status_message": translateString("Lines successfully reconcilied with transactions."),
})
