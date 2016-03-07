is_source = context.AccountingTransaction_isSourceView()
total_debit = 0
for line in context.getMovementList(
      portal_type=context.getPortalAccountingMovementTypeList()):
  if is_source:
    total_debit += line.getSourceInventoriatedTotalAssetDebit()
  else:
    total_debit += line.getDestinationInventoriatedTotalAssetDebit()

return total_debit
