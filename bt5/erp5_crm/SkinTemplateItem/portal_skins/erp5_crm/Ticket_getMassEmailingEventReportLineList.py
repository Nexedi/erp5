portal = context.getPortalObject()

count = portal.portal_catalog.countResults

total_events = count(follow_up_uid=context.getUid(),
  portal_type="Mail Message",
  simulation_state=("received", "delivered", "started"))[0][0]
total_opened = count(follow_up_uid=context.getUid(),
  portal_type="Mail Message",
  simulation_state=("received", "delivered"))[0][0]
total_read = count(follow_up_uid=context.getUid(),
  portal_type="Mail Message", simulation_state="delivered")[0][0]

if total_events > 0:
  line = context.newContent(temp_object=1, total_event_sent=total_events,
    total_event_received=total_opened,
    total_event_received_percent=float(total_opened)/float(total_events)*100,
    total_event_delivered=total_read,
    total_event_delivered_percent=float(total_read)/float(total_events)*100)
  return line,
else:
  return []
