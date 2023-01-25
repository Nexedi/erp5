if brain is not None:
  transaction = brain.getObject()
else:
  transaction = context

def getTotalPrice(transaction_path):
  is_source = transaction.AccountingTransaction_isSourceView()
  total_price = 0
  for mvt in transaction.getMovementList(
         portal_type=context.getPortalAccountingMovementTypeList()):
    if is_source:
      node = mvt.getSourceValue()
      if node is not None and node.isMemberOf('account_type/asset/cash'):
        total_price -= mvt.getSourceInventoriatedTotalAssetPrice() or 0
    else:
      node = mvt.getDestinationValue()
      if node is not None and  node.isMemberOf('account_type/asset/cash'):
        total_price -= mvt.getDestinationInventoriatedTotalAssetPrice() or 0
  return total_price

return getTotalPrice(transaction.getPath())
