portal = context.getPortalObject()
record = context

if record.getDestinationReference() is not None:
  ticket_brain_list = portal.portal_catalog(
    portal_type="Leave Request",
    reference=record.getDestinationReference(),
    )
  if len(ticket_brain_list) != 1:
    raise ValueError("Incorrect number of follow_up ticket found for the Record")
  ticket = ticket_brain_list[0].getObject()
else:
  # No destination reference means no ticket to track it server side: Create a new one
  record.Event_createFollowUpTicket(
    follow_up_ticket_title=record.getTitle(),
    follow_up_ticket_type="Leave Request",
  )
  ticket = record.getFollowUpValue()
  ticket.setDestination(record.getSource())
  ticket.setResource(record.getResource())
  ticket.plan()
record.setDestinationReference(ticket.getReference())

record.setFollowUpValue(ticket)

ticket.edit(
  title="Cong\xc3\xa9 " + record.getSourceTitle(),
  # XXX resource=record.getResource(),
  #start_date=DateTime(record.getStartDate()),
  #stop_date=DateTime(record.getStopDate()),
  #animation_center=record.getSite(),
  #travel_destination=record.getDestinationNodeTitle(),
  # XX Hackish
  description=record.getComment(),
  )

line_list = ticket.objectValues(portal_type="Leave Request Period")
if len(line_list) == 0:
  line = ticket.newContent(
    portal_type="Leave Request Period"
    )
elif len(line_list) == 1:
  line = line_list[0]
else:
  raise ValueError("incorrect number of Leave Request Period in %s" % ticket.getRelativeUrl())

line.edit(
  start_date=DateTime(record.getStartDate()),
  stop_date=DateTime(record.getStopDate()).latestTime(),
  resource=record.getResource(),
  )

record.deliver()

ticket.LeaveRequest_createRepresentativeRecord(
  record_relative_url=record.getRelativeUrl()
  )

return ticket
