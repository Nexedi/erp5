from Products.ERP5Type.Message import translateString

portal = sci['object'].getPortalObject()
bank_reconciliation = sci['object']

# We activate after BankReconciliation_selectNonReconciledTransactionList, in
# case the user cancels just after using this action.
portal.portal_catalog.activate(
  activity='SQLQueue', after_tag='BankReconciliation_selectNonReconciledTransactionList'
).searchAndActivate(
  portal_type=portal.getPortalAccountingMovementTypeList(),
  default_aggregate_uid=bank_reconciliation.getUid(),
  method_args=(bank_reconciliation.getRelativeUrl(), translateString('Cancelling bank reconciliation')),
  method_id='AccountingTransactionLine_removeBankReconciliation'
)
