from Products.ERP5Type.Message import translateString

context.getPortalObject().setPlacelessDefaultReindexParameters(activate_kw=dict(tag=tag))

# XXX maybe we want to distribute this more.
# At the moment we cannot use searchAndActivate from Inventory API query
for line in context.BankReconciliation_getAccountingTransactionLineList():
  line.AccountingTransactionLine_setBankReconciliation(context, 
      message=translateString("Select Non Reconciled Transactions"))
