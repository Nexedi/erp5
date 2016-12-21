portal = context.getPortalObject()
record = context

if record.getDestinationReference() is not None:
  ticket_brain_list = portal.portal_catalog(
    portal_type="Travel Request",
    reference=record.getDestinationReference(),
    )
  if len(ticket_brain_list) != 1:
    raise ValueError("Incorrect number of follow_up ticket found for the Record")
  ticket = ticket_brain_list[0].getObject()
else:
  # No destination reference means no ticket to track it server side: Create a new one
  record.Event_createFollowUpTicket(
    follow_up_ticket_title=record.getTitle(),
    follow_up_ticket_type="Travel Request",
  )
  ticket = record.getFollowUpValue()

record.setDestinationReference(ticket.getReference())

record.setFollowUpValue(ticket)

ticket.edit(
  title=record.getTitle(),
  #resource=record.getSource(),
  start_date=DateTime(record.getStartDate()),
  stop_date=DateTime(record.getStopDate()),
  animation_center=record.getSite(),
  travel_destination=record.getDestinationNodeTitle(),
  # XX Hackish
  description=record.getComment(),
  )

record.deliver()

ticket.TravelRequest_createRepresentativeRecord(
  record_relative_url=record.getRelativeUrl()
  )

return ticket
