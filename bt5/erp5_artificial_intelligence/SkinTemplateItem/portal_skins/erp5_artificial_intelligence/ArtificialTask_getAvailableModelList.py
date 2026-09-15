from Products.ERP5Type.Cache import CachingMethod



def getModelList():
  conn = context.ArtificialTask_getDefaultConnector()
  return [(x, x) for x in conn.getModelList()]



getModelList = CachingMethod(getModelList,
      id=('ArtificialTask_getAvailableModelList',),
      cache_factory='erp5_content_long')

return getModelList()
