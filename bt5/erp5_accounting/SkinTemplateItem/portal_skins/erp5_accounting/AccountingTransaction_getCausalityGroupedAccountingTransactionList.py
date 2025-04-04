"""Returns the group of accounting transaction related by causality
"""
portal = context.getPortalObject()
accounting_transaction_type_list = \
              portal.getPortalAccountingTransactionTypeList()
accounting_transaction_set = {}
accounting_transaction_to_check_list = [context]

# Add all causality transactions
while accounting_transaction_to_check_list:
  accounting_transaction = accounting_transaction_to_check_list.pop()
  if accounting_transaction not in accounting_transaction_set:
    accounting_transaction_set[accounting_transaction] = 1

    for related_causality in accounting_transaction.getCausalityRelatedValueList(
                portal_type=accounting_transaction_type_list) + accounting_transaction.getCausalityValueList(
                portal_type=accounting_transaction_type_list):
      if related_causality.getSimulationState() not in ('cancelled', 'deleted'):
        accounting_transaction_to_check_list.append(related_causality)

return accounting_transaction_set.keys()
