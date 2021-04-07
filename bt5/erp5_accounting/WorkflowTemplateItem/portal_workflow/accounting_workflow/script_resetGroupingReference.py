"""When transaction is restarted, we'll unset existing grouping references on lines.
"""
transaction = sci['object']
for line in transaction.getMovementList(
   portal_type=sci.getPortal().getPortalAccountingMovementTypeList()):
  line.AccountingTransactionLine_resetGroupingReference()
