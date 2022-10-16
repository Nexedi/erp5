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
  if portal.portal_workflow.isTransitionPossible(ticket, 'validate'):
    ticket.validate()

record.setDestinationReference(ticket.getReference())

record.setFollowUpValue(ticket)

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
  resource=record.getResource(),
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
