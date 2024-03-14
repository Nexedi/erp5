sm = context.getDeliveryRelatedValue(portal_type="Simulation Movement")
if sm is None:
  return None
sm = sm.getParentValue().getParentValue()
if context.getPortalType() == "Invoice Line":
  sm = sm.getParentValue().getParentValue()
if sm.getPortalType() != "Simulation Movement":
  return None
order_line = sm.getDeliveryValue()
return order_line.getIntIndex()
