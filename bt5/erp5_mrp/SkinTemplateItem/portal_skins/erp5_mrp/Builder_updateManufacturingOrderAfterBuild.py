assert context.getPortalType() == "Manufacturing Order"
portal = context.getPortalObject()

# XXX, the API is weird, we can get movement_list as parameter of this script, but movement_list is not filtered
# by the generated order in the case we have several distinct orders generated. So we will filter movements ourself
# for now
assert len(movement_list) > 0

# We assume no variation here
new_movement_list = []
resource_set = set([x.getResource() for x in context.getMovementList()])
for movement in movement_list:
  if movement.getResource() in resource_set:
    new_movement_list.append(movement)
movement_list = new_movement_list
assert len(movement_list)

# This is not a loop
while context.getSimulationState() == "draft":
  context.plan()
  # Make sure to erase the date set by init script
  context.setStartDate(None)
  # The following is to check if it should be confirmed automatically.
  # Only if not other Manufacturing Order for the same element has been done.
  child_list = context.objectValues()
  if child_list:
    child = child_list[0]
    # Set Production Order as Causality if needed
    causality = child.getCausalityValue(portal_type="Production Packing List")
    if causality:
      production_order = causality.getCausalityValue()
      context.setCausalityValue(production_order)
      # Confirm if no other Manufacturing Orders are related to Production Order
      sibling_list = portal.portal_catalog(
        portal_type="Manufacturing Order",
        strict_causality_uid=production_order.getUid(),
        simulation_state="confirmed",
      )
      if sibling_list:
        break
  context.confirm()
  break
# XXX Not ideal way to set date. In particular, if a production was cancelled, we might still
# have a start_date or stop_date corresponding to it. Like if you have a production order
# in july, annother one in august, you might have purhcase order in july. But if you cancel
# production order of july, then the purchase will still be in juny while it can be shifted
# to july.
for property_name in ('start_date', 'stop_date'):
  property_value_list = []
  delivery_property_value = context.getProperty(property_name)
  if delivery_property_value:
    property_value_list.append(delivery_property_value)
  for movement in movement_list:
    property_value_list.append(movement.getProperty(property_name))
  property_value = min(property_value_list)
  assert property_value is not None
  context.setProperty(property_name, property_value)
