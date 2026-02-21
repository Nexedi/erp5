portal = context.getPortalObject()
translateString = context.Base_translateString
accounting_movement_type_list = context.getPortalAccountingMovementTypeList()

for line in listbox:
  bank_reconciliation_line_value = portal.restrictedTraverse(line["listbox_key"])
  previous_related_accounting_transaction_value = \
    bank_reconciliation_line_value.getAggregateRelatedValue(portal_type=accounting_movement_type_list)

  related_accounting_transaction_uid = line.get("aggregate_related_title", None)
  if related_accounting_transaction_uid is None:
    if previous_related_accounting_transaction_value is not None:
      previous_related_accounting_transaction_value.AccountingTransactionLine_removeBankReconciliation(
        bank_reconciliation_relative_url=bank_reconciliation_line_value.getRelativeUrl(),
        message=translateString("Unreconciling Bank Line"),
      )
    continue

  related_accounting_transaction_value = portal.portal_catalog.getObject(related_accounting_transaction_uid)
  if previous_related_accounting_transaction_value.getRelativeUrl() != related_accounting_transaction_value.getRelativeUrl():
    previous_related_accounting_transaction_value.AccountingTransactionLine_removeBankReconciliation(
      bank_reconciliation_relative_url=bank_reconciliation_line_value.getRelativeUrl(),
      message=translateString("Unreconciling Bank Line"),
    )
    related_accounting_transaction_value.AccountingTransactionLine_addBankReconciliation(
      bank_reconciliation_relative_url=bank_reconciliation_line_value.getRelativeUrl(),
      message=translateString("Reconciling Bank Line"),
    )

# Since setting aggregate-related can change which lines are simulated, update simulation
context.updateSimulation(expand_root=1)

return context.Base_redirect("view", keep_items={
  "portal_status_message": translateString("Lines successfully reconcilied with transactions."),
})
