"""Returns the possible ledger for this delivery.

This will return only ledgers allowed in the delivery type definition.
"""

portal = context.getPortalObject()

ledger_item_list = context.Base_getPreferredCategoryChildItemList(portal.portal_categories.ledger)
allowed_ledger_list = portal.portal_types[context.getPortalType()].getLedgerList()

return [('', '')] + [item for item in ledger_item_list if item[1] in allowed_ledger_list]
