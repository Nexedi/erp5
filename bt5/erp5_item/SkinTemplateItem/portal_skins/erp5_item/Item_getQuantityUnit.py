from Products.ERP5Type.Log import log
log('Depracated usage of Item_getQuantityUnit, please use Item_getQuantityUnitItemList instead')
return context.Item_getQuantityUnitItemList()
