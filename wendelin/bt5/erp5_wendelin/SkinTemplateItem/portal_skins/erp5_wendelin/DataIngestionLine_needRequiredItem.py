result = False
if context.getQuantity() != 0:
  resource_value = context.getResourceValue()
  if resource_value and len(resource_value.getRequiredAggregatedPortalTypeList()):
    result = True
return result
