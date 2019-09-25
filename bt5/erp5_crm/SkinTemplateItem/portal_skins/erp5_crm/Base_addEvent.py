"""Generic script of Entity_addEvent
It creates new Event for any context which become follow_up of created Event.

Connected user is source (outgoing direction)
for Organisations and Persons, context is destination(_section) (for outgoing direction)

Follow_up is setted up only if context is not Entity.

User is redirected on Event to fill in message.
"""
portal = context.getPortalObject()
portal_entity_type_list = portal.getPortalEntityTypeList()

# Search current user ID
logged_in_user_value = portal.portal_membership.getAuthenticatedMember().getUserValue()
start_date = DateTime()

organisation = None
person = None
if logged_in_user_value is not None:
  person = logged_in_user_value.getRelativeUrl()
  organisation = logged_in_user_value.getSubordination()

person_relative_url = None
organisation_relative_url = None
if context.getPortalType() in portal_entity_type_list:
  if context.getPortalType() == 'Person':
    person_relative_url = context.getRelativeUrl()
    organisation_relative_url = context.getSubordination()
  elif context.getPortalType() == 'Organisation':
    person_relative_url = None
    organisation_relative_url = context.getRelativeUrl()
else:
  follow_up = context.getRelativeUrl()

# XXX if source or destination is explicitcy choosen, what should be
# source_section or destination_section ???

if direction == 'outgoing':
  source_url = source or person
  source_section_url = organisation
  destination_url = destination or person_relative_url or organisation_relative_url
  destination_section_url = organisation_relative_url
elif direction == 'incoming':
  source_url = source or person_relative_url or organisation_relative_url
  source_section_url = organisation_relative_url
  destination_url = destination or person
  destination_section_url = organisation
else:
  raise NotImplementedError, 'The specified direction is not handled: %r' % (direction,)

event_kw = {
  'portal_type' : portal_type,
  'title' : title,
  'resource' : resource,
  'source' : source_url,
  'source_section' : source_section_url,
  'destination' : destination_url,
  'destination_section' : destination_section_url,
  'start_date' : start_date,
  'follow_up' : follow_up,
  'text_content' : text_content,
  'content_type' : portal.portal_preferences.getPreferredTextEditor() and 'text/html' or 'text/plain',
  }
# Create event
module = portal.getDefaultModule(portal_type=portal_type)
event = module.newContent(**event_kw)

if notification_message:
  event.Event_setTextContentFromNotificationMessage(
     reference=notification_message, language=language)

if not keep_draft:
  if direction == 'incoming':
    # Support event_workflow and event_simulation_workflow
    if portal.portal_workflow.isTransitionPossible(event, 'receive'):
      event.receive()
    if portal.portal_workflow.isTransitionPossible(event, 'stop'):
      event.stop()
  else:
    event.plan()

if batch_mode:
  return event

message = portal.Base_translateString('New event created.')

return event.Base_redirect(keep_items={'portal_status_message': message})
