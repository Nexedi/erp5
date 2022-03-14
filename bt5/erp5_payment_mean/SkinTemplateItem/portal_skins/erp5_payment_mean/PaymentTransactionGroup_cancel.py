if REQUEST is not None:
  return

for payment_transaction_line in context.getAggregateRelatedValueList():
  payment_transaction_line.setDefaultActivateParameterDict({"tag": tag})
  payment_transaction_line.setAggregate(None, portal_type=context.getPortalType())
