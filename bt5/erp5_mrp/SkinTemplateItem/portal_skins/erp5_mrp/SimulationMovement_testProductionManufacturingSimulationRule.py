movement = context
result = False
parent = movement.getParentValue()
if parent.getPortalType() == 'Applied Rule' and movement.getSpecialiseValue(portal_type="Transformation"):
  grand_parent = parent.getParentValue()
  if grand_parent.getPortalType() == "Simulation Movement" and \
      grand_parent.getDeliveryValue() and \
      grand_parent.getDeliveryValue().getPortalType() == "Production Order Line":
    resource_value = context.getResourceValue()
    if resource_value:
      result = (len(resource_value.getAggregatedPortalTypeList()) != 0) and \
                 ("production" in resource_value.getUseList())
return result
