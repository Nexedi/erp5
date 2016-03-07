"""When transaction is restarted, we'll break existing grouping references on lines.
"""
transaction = sci['object']
for line in transaction.getMovementList(
   portal_type=sci.getPortal().getPortalAccountingMovementTypeList()):
  if line.getGroupingReference():
    line.activate(
       after_tag='accounting_grouping_reference'
       ).AccountingTransactionLine_resetGroupingReference()
