from Products.CMFActivity.ActiveResult import ActiveResult
portal = context.getPortalObject()

tracking_list = list(reversed(portal.portal_simulation.getCurrentTrackingList(aggregate_uid=context.getUid())))
if tracking_list:
  delivery_dict = {
      x.uid: x.getObject()
      for x in portal.portal_catalog(
          uid=[x.delivery_uid for x in tracking_list],
      )
  }
  for previous_brain, next_brain in zip(tracking_list, tracking_list[1:]):
    if delivery_dict[previous_brain.delivery_uid].getDestination() != delivery_dict[next_brain.delivery_uid].getSource():
      portal.restrictedTraverse(active_process).postResult(
       ActiveResult(summary=script.getId(),
           detail='%s has tracking error' % context.getRelativeUrl(),
           result='',
           severity=100))
