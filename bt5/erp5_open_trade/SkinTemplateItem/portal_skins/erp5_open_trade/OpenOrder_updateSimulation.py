subscription_item_set = set()

for open_order_line in context.objectValues():
  for ob in [open_order_line] + open_order_line.getCellValueList():
    for item in ob.getAggregateValueList():
      if getattr(item.aq_explicit, 'updateSimulation', None) is not None and \
          item not in subscription_item_set:
        subscription_item_set.add(item)
        item.updateSimulation(expand_root=1)
