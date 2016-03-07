from Products.ERP5Type.Cache import CachingMethod

def Movement_lookupPrice():
  resource = context.getResourceValue()
  if resource is not None:
    return resource.getPrice(context=context)
  else:
    return None

return CachingMethod(Movement_lookupPrice, ('erp5_banking_core/Movement_lookupPrice', context.getResource()), 
                     cache_factory="erp5_ui_long")()
