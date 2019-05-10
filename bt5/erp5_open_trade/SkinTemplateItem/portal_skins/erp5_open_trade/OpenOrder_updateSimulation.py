subscription_item_set = set()
portal = context.getPortalObject()

def hasUpdateSimulationActivity(item):
  for activity in portal.portal_activities.getMessageList(
     method_id="_updateSimulation", path="/erp5/" + item.getRelativeUrl()):
    if activity.kw == {"expand_root" : 1}:
      return True

  return False

for open_order_line in context.objectValues():
  for ob in [open_order_line] + open_order_line.getCellValueList():
    for item in ob.getAggregateValueList():
      if getattr(item.aq_explicit, 'updateSimulation', None) is not None and \
          item not in subscription_item_set:
        subscription_item_set.add(item)
        # Optmise for not launch an activity when some activity
        # is there already pending for the same purpose.
        if not hasUpdateSimulationActivity(item):
          if getattr(item.aq_explicit, 'updateExpandableRootSimulation', None):
            # If this method is implemented use activate to only execute it
            # once.
            item.activate().updateExpandableRootSimulation()
          else:
            item.updateSimulation(expand_root=1)
