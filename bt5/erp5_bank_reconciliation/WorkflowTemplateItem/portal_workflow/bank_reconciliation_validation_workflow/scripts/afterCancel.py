from Products.ERP5Type.Message import translateString

portal = sci['object'].getPortalObject()

# We activate after BankReconciliation_selectNonReconciledTransactionList, in
# case the user cancels just after using this action. 
portal.portal_catalog.activate(
  queue='SQLQueue', after_tag='BankReconciliation_selectNonReconciledTransactionList'
).searchAndActivate(
  portal_type=portal.getPortalAccountingMovementTypeList(),
  default_aggregate_uid=sci['object'].getUid(),
  method_args=(None, translateString('Cancelling bank reconciliation')),
  method_id='AccountingTransactionLine_setBankReconciliation'
)
