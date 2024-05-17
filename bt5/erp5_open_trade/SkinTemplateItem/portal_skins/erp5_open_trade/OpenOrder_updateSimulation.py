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

        # Logic duplicated from SubscriptionItem.py
        start_date = ob.getStartDate()
        # if there is no stop_date, block the generation
        # to today
        stop_date = ob.getStopDate()
        current_date = start_date
        if (start_date == stop_date) or (stop_date is None):
          # stop_date seems acquired from start_date
          stop_date = now
        while current_date < stop_date:
          current_date = item.getNextPeriodicalDate(current_date)

        # Do not expand subscription item if there is
        # no new simulation movement to create
        # (expand always reindex the full simulation tree,
        # which can be cpu costly when we have many hosting subscription)
        simulation_movement_list = portal.portal_simulation.getMovementHistoryList(
          portal_type='Simulation Movement',
          aggregate__uid=item.getUid(),
          from_date=current_date,
          at_date=current_date,
          only_accountable=False,
        )
        if len(simulation_movement_list) == 0:
          item.updateSimulation(expand_root=1)
