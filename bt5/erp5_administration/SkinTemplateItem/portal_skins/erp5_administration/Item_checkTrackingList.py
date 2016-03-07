from Products.CMFActivity.ActiveResult import ActiveResult
portal = context.getPortalObject()

tracking_list = list(reversed(portal.portal_simulation.getCurrentTrackingList(aggregate_uid=context.getUid())))

for previous_brain, next_brain in zip(tracking_list, tracking_list[1:]):
  previous_delivery = portal.portal_catalog.getObject(previous_brain.delivery_uid)
  next_delivery = portal.portal_catalog.getObject(next_brain.delivery_uid)
  
  if previous_delivery.getDestination() != next_delivery.getSource():
    portal.restrictedTraverse(active_process).postResult(
     ActiveResult(summary=script.getId(),
         detail='%s has tracking error' % context.getRelativeUrl(),
         result='',
         severity=100))
