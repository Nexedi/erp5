is_source = context.AccountingTransaction_isSourceView()
total_credit = 0
for line in context.getMovementList(
      portal_type=context.getPortalAccountingMovementTypeList()):
  if is_source:
    total_credit += line.getSourceInventoriatedTotalAssetCredit()
  else:
    total_credit += line.getDestinationInventoriatedTotalAssetCredit()

return total_credit
