"""Returns the event that caused this ticket.

Either defined explictly through causality relation or simply the first event.
"""
portal = context.getPortalObject()

causality = context.getCausalityValue(portal_type=portal.getPortalEventTypeList())
if causality is not None:
  return causality

# XXX for folder workflow action dialog
if context.isTempObject():
  context = portal.restrictedTraverse(context.getRelativeUrl())

event_list = portal.portal_catalog(
  portal_type=portal.getPortalEventTypeList(),
  default_follow_up_uid=context.getUid(),
  limit=1,
  sort_on=(('delivery.start_date', 'ASC'),),
)
if event_list:
  return event_list[0].getObject()
