portal_type_list = context.getPortalAccountingTransactionTypeList()
Base_translateString = context.Base_translateString

item_list = []
for portal_type in portal_type_list :
  item_list.append((Base_translateString(portal_type), portal_type))

return item_list
