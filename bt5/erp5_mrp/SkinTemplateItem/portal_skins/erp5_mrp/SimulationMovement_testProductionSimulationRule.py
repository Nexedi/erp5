movement = context
result = False
parent = movement.getParentValue()
if parent.getPortalType() == 'Applied Rule' and movement.getSpecialiseValue(portal_type="Transformation"):
  grand_parent = parent.getParentValue()
  if grand_parent.getPortalType() == "Simulation Movement" and \
      grand_parent.getDeliveryValue() and \
      grand_parent.getDeliveryValue().getPortalType() == "Production Order Line":
    resource_value = grand_parent.getDeliveryValue().getResourceValue()
    result = resource_value is not None
return result
