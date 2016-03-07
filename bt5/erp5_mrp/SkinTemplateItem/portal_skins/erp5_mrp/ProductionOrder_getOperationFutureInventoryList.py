"""Returns list of services' inventories used in consumption for production"""
kwargs['resource_portal_type'] = context.getPortalObject().getPortalServiceTypeList()
return context.ProductionOrder_getConsumptionMovementList(*args,**kwargs)
