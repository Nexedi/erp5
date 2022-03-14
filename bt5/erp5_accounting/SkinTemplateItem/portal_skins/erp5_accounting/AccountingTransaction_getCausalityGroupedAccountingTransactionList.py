"""Returns the group of accounting transaction related by causality
"""
portal = context.getPortalObject()
accounting_transaction_type_list = \
              portal.getPortalAccountingTransactionTypeList()
accounting_transaction_set = {}
accounting_transaction_set[context] = 1

# Add all causality transactions
for accounting_transaction in [context] + context.getCausalityValueList(
                  portal_type=accounting_transaction_type_list):
  accounting_transaction_set[accounting_transaction] = 1
  for related_causality in accounting_transaction.getCausalityRelatedValueList(
              portal_type=accounting_transaction_type_list):
    if related_causality.getSimulationState() not in ('cancelled', 'deleted'):
      accounting_transaction_set[related_causality] = 1

return list(accounting_transaction_set.keys())
