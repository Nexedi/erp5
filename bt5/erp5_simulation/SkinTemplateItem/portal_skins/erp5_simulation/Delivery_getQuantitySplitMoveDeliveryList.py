"""
Returns all deliveries that could be used to get quantities of current delivery.
This is used when we want to split a quantity of delivery line and make sure that
the new line will go to a given delivery.
"""
portal = context.getPortalObject()
current_delivery = context
current_delivery_portal_type = current_delivery.getPortalType()
current_delivery_uid = current_delivery.getUid()
delivery_list = []
reserved_inventory_state_list = portal.getPortalReservedInventoryStateList()

for causality_value in current_delivery.getCausalityValueList():
  for delivery in causality_value.getCausalityRelatedValueList(
      portal_type=current_delivery_portal_type):
    if delivery.getUid() != current_delivery_uid:
      if delivery.getSimulationState() in reserved_inventory_state_list:
        delivery_list.append(delivery)
return delivery_list
