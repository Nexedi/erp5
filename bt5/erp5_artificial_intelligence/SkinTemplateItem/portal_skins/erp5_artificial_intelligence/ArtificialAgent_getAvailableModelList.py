from Products.ERP5Type.Cache import CachingMethod

conn = context.getConnectorValue()

if not conn:
  return []

def getModelList():
  return conn.getModelList()



getModelList = CachingMethod(getModelList,
      id=('ArtificialAgent_getAvailableModelList', conn.getRelativeUrl()),
      cache_factory='erp5_content_long')

return getModelList()
