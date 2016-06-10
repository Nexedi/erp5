"""Returns the item list of ledgers defined on Accounting Types
"""
portal = context.getPortalObject()
portal_types = portal.portal_types

accounting_type_list = portal.getPortalAccountingTransactionTypeList()
ledger_set = set()

for accounting_type in accounting_type_list:
  try:
    new_ledger_list = portal_types[accounting_type].getLedgerValueList([])
    ledger_set = ledger_set.union(set(new_ledger_list))
  except AttributeError:
    # This portal type doesn't inherit from Delivery Type, thus we can pass
    continue

if len(ledger_set):
  return [[ledger.getTranslatedTitle(), ledger.getRelativeUrl()] for ledger in list(ledger_set)]

return ()
