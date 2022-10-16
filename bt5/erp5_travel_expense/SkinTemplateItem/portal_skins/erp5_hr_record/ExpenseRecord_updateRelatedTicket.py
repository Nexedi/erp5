import base64
import json
import six
portal = context.getPortalObject()
record = context

def byteify(string):
  if isinstance(string, dict):
    tmp = {}
    for key, value in six.iteritems(string):
      tmp[byteify(key)] = byteify(value)
    return tmp
  elif isinstance(string, list):
    return [byteify(element) for element in string]
  elif isinstance(string, unicode):
    return string.encode('utf-8')
  else:
    return string

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
  if portal.portal_workflow.isTransitionPossible(ticket, 'validate'):
    ticket.validate()

record.setDestinationReference(ticket.getReference())
record.setFollowUpValue(ticket)

related_mission_url = record.getRelatedMissionUrl()
if related_mission_url:
  travel_request = context.restrictedTraverse(related_mission_url)
  source_project_url = travel_request.getFollowUp()
else:
  source_project_url = ""

new_transition_comment =  record.getTransitionComment()
if new_transition_comment is not None:
  new_transition_comment = byteify(json.loads(new_transition_comment))
  old_transition_comment = byteify(json.loads(ticket.Ticket_generateTransitionAndCommentList(listbox_view=False)))
  for attr in new_transition_comment:
    if attr not in old_transition_comment:
      context.log(new_transition_comment)
      context.log(old_transition_comment)
      if portal.portal_workflow.isTransitionPossible(ticket, 'validate'):
        ticket.validate(comment=new_transition_comment[attr]['comment'], actor=new_transition_comment[attr]['actor'])
ticket.edit(
  title=record.getTitle(),
  resource=record.getType(),
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
  source_project=source_project_url,
  source_section=record.getSourceValue().getCareerSubordination()
  )

publication_section = portal.ERP5Site_getPreferredExpenseDocumentPublicationSectionValue()
photo_data = record.getPhotoData()
if photo_data:
  if "," in photo_data and ticket:
    photo_type, photo_data = photo_data.split(",")
    filename="tmp.png"
    # XXX This is getting more hackish
    if "application/pdf" in photo_type:
      filename="tmp.pdf"
    image = portal.portal_contributions.newContent(
      data = base64.b64decode(photo_data),
      reference=ticket.getReference()+ "-justificatif",
      title = ticket.getReference() + " Justificatif",
      description = ticket.getDescription(),
      filename=filename,
      follow_up=ticket.getRelativeUrl(),
      publication_section=publication_section.getRelativeUrl(),
      group=ticket.getDestinationDecisionValue().getGroup()
    )
    image.share()

record.deliver()

# Probably should leave the interaction do this
ticket.ExpenseValidationRequest_createRepresentativeRecord(
  record_relative_url=record.getRelativeUrl()
  )

return ticket
