"""Returns the possible ledger for this delivery.

This will return only ledgers allowed in the delivery type definition.
"""

portal = context.getPortalObject()

ledger_item_list = context.Base_getPreferredCategoryChildItemList(portal.portal_categories.ledger)

type_info = portal.portal_types[context.getPortalType()]
if getattr(type_info, 'getLedgerList', None) is not None:
  allowed_ledger_list = type_info.getLedgerList()
  return [('', '')] + [item for item in ledger_item_list if item[1] in allowed_ledger_list]
else:
  return ledger_item_list
