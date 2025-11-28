"""
To get accounting reports right, Balance Transactions must be
indexed in order.

This script does not assume that Balance Transactions are already
available in the catalog, though this assumption should hold when
launched by `ERP5Site_reindexAll`.
"""

portal = context.getPortalObject()

accounting_module = portal.accounting_module
balance_transaction_list = accounting_module.objectValues(
  portal_type='Balance Transaction'
)
balance_transaction_by_date_list = sorted(
  balance_transaction_list,
  key=lambda balance_transaction: balance_transaction.getStartDate(),
)

previous_tag = None

for balance_transaction_value in balance_transaction_by_date_list:
  tag = 'AccountingModule_reindexBalanceTransactionList:%i' % \
    balance_transaction_value.getUid()
  activate_kw = {'tag': tag}
  if previous_tag is not None:
    activate_kw['after_tag'] = previous_tag
  previous_tag = tag
  balance_transaction_value.recursiveReindexObject(activate_kw=activate_kw)

accounting_module.activate(
  tag=final_activity_tag,
  after_tag=previous_tag,
).getId()
