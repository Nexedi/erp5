"""Returns the item list of ledgers defined on Accounting Types
"""
portal = context.getPortalObject()
portal_types = portal.portal_types

ledger_set = set()

ledger_item_list = context.Base_getPreferredCategoryChildItemList(
  portal.portal_categories.ledger, base=True)

for accounting_type in portal.getPortalAccountingTransactionTypeList():
  ledger_set.update(portal_types[accounting_type].getLedgerList(base=True))

return [item for item in ledger_item_list if item[1] in ledger_set]
