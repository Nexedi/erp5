from Products.ERP5Type.Cache import CachingMethod

def getCheckbookTypeItemList():
  return [('', '')] + [(x.getTitle(), x.getRelativeUrl())
    for x in context.checkbook_type_module.objectValues()]

getCheckbookTypeItemList = CachingMethod(getCheckbookTypeItemList, 
                                         id = 'Baobab_getCheckbookTypeItemList', 
                                         cache_factory = 'erp5_ui_medium')
return getCheckbookTypeItemList()
