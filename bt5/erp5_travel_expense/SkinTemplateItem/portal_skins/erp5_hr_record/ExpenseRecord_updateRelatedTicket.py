portal = context.getPortalObject()
record = context

if record.getDestinationReference() is not None:
  ticket_brain_list = portal.portal_catalog(
    portal_type="Expense Validation Request",
    reference=record.getDestinationReference(),
    )
  if len(ticket_brain_list) != 1:
    raise ValueError("Incorrect number of follow_up ticket found for the Record")
  ticket = ticket_brain_list[0].getObject()
else:
  # No destination reference means no ticket to track it server side: Create a new one
  record.Event_createFollowUpTicket(
    follow_up_ticket_title=record.getComment(),
    follow_up_ticket_type="Expense Validation Request",
  )
  ticket = record.getFollowUpValue()

record.setDestinationReference(ticket.getReference())

record.setFollowUpValue(ticket)

related_mission_url = record.getRelatedMissionUrl()
if related_mission_url:
  travel_request = context.restrictedTraverse(related_mission_url)
  source_project_url = travel_request.getFollowUp()
else:
  source_project_url = ""
ticket.edit(
  title=record.getTitle(),
  #resource=record.getSource(),
  start_date=DateTime(record.getDate()),
  stop_date=DateTime(record.getDate()),
  # Specific
  quantity=1.0,
  quantity_unit="unit",
  price=record.getQuantity(),
  price_currency=record.getResource(),
  description=record.getComment(),
  latitude=record.getLatitude(),
  longitude=record.getLongitude(),
  source_project=source_project_url
  )
photo_data = record.getPhotoData()
if photo_data:
  ticket.setPhotoData(photo_data)

record.deliver()

# Probably should leave the interaction do this
ticket.ExpenseValidationRequest_createRepresentativeRecord(
  record_relative_url=record.getRelativeUrl()
  )

return ticket
