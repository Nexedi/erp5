from Products.ERP5Type.Cache import CachingMethod

conn = context.ArtificialTask_getDefaultConnector()

def getModelList():
  return [(x, x) for x in conn.getModelList()]



getModelList = CachingMethod(getModelList,
      id=('ArtificialTask_getAvailableModelList', conn.getRelativeUrl()),
      cache_factory='erp5_content_long')

return getModelList()
