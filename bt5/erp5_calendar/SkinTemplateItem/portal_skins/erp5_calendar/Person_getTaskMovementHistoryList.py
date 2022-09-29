person = context

acceptable_state_list = context.getPortalFutureInventoryStateList() + \
                        context.getPortalReservedInventoryStateList() + \
                        context.getPortalTransitInventoryStateList() + \
                        context.getPortalCurrentInventoryStateList()

movement_list = context.portal_simulation.getMovementHistoryList(
                   node_uid=person.getUid(),
                   portal_type=portal_type,
                   simulation_state=acceptable_state_list,
                   to_date=to_date,
                   from_date=from_date,
                   omit_mirror_date=0,
)


# XXX It is a bad idea to return order_value or delivery_value,
# because same object can be displayed multiple time in some cases

return_list = []

# Normally, simulation movement should only have 1 order value
for mvt_obj in movement_list:
  # XXX Can't we use a brain instead ?
  if mvt_obj.portal_type == "Simulation Movement":
    obj = mvt_obj.getOrderValue()
    if obj is not None:
      mvt_obj = obj
  return_list.append(mvt_obj)

return return_list
