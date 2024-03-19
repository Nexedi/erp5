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
        # If start_date is in futur, do not look for unreachable period
        stop_date = item.getNextPeriodicalDate(max(now, ob.getStartDate()))
        # Do not expand subscription item if there is
        # no new simulation movement to create
        # (expand always reindex the full simulation tree,
        # which can be cpu costly when we have many hosting subscription)
        simulation_movement_list = portal.portal_simulation.getMovementHistoryList(
          portal_type='Simulation Movement',
          aggregate__uid=item.getUid(),
          from_date=stop_date,
          at_date=stop_date,
          only_accountable=False,
        )
        if len(simulation_movement_list) == 0:
          item.updateSimulation(expand_root=1)
