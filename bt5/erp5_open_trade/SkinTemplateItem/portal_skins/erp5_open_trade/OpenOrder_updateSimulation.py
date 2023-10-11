if context.checkConsistency():
  # Skip if open order is not consistency
  return

subscription_item_set = set()
now = DateTime().earliestTime()
portal = context.getPortalObject()

for open_order_line in context.objectValues():
  for ob in [open_order_line] + open_order_line.getCellValueList():
    for item in ob.getAggregateValueList():
      if getattr(item.aq_explicit, 'updateSimulation', None) is not None and \
          item not in subscription_item_set:
        subscription_item_set.add(item)
        stop_date = item.getNextPeriodicalDate(now)
        # Do not expand subscription item if there is
        # no new simulation movement to create
        # (expand always reindex the full simulation tree,
        # which can be cpu costly when we have many hosting subscription)
        simulation_movement = portal.portal_catalog.getResultValue(
          portal_type="Simulation Movement",
          aggregate__uid=item.getUid(),
          **{'movement.stop_date': stop_date}
        )
        if simulation_movement is None:
          item.updateSimulation(expand_root=1)
