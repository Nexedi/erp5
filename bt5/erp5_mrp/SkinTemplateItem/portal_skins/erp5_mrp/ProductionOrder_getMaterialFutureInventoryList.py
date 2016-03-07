"""Returns list of products' inventories used in consumption for production"""
kwargs['resource_portal_type'] = context.getPortalObject().getPortalProductTypeList()
return context.ProductionOrder_getConsumptionMovementList(*args,**kwargs)
