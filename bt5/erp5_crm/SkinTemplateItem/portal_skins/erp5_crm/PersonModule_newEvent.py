"""
  This script creates a new event with given metadata and
  attaches it to the current ticket.
"""
translateString = context.Base_translateString
module = context.getDefaultModule(portal_type)

# Build selection
person_list = context.portal_selections.getSelectionCheckedValueList(selection_name)
if not person_list:
  person_list = context.portal_selections.callSelectionFor(selection_name)

# Find authenticated user
user_person = context.portal_membership.getAuthenticatedMember().getUserValue()

event_list = []
# For every person, create an event
if not single_event:
  count = 0
  for person in person_list:
    # Create a new event
    event = module.newContent(portal_type=portal_type, 
                            description=description, 
                            title=title, 
                            follow_up=follow_up,
                            text_content=text_content) # text_format is set by Event_init
    count += 1
    # Trigger appropriate workflow action
    if direction == 'incoming':
      event.setSourceValue(person.getObject())
      event.setDestinationValue(user_person)
    else:
      event.setDestinationValue(person.getObject())
      event.setSourceValue(user_person)
    event.plan()
    event_list.append(event)
else:
  if direction == 'incoming' and len(person_list) > 1:
    # This case is not possible
    portal_status_message = translateString(
             "The single event option can only be used with outgoing messages.")
    return context.Base_redirect(form_id, keep_items = dict(portal_status_message=portal_status_message, selection_name=selection_name), **kw)
  # Proceed to event creation
  event = module.newContent(portal_type=portal_type, 
                            description=description, 
                            title=title, 
                            follow_up=follow_up,
                            text_content=text_content) # text_format is set by Event_init
  event.setDestinationValueList([person.getObject() for person in person_list])
  event.setSourceValue(user_person)
  event.plan()
  count = 1
  event_list.append(event)

if batch_mode:
  return event_list

portal_status_message = translateString("Created and associated ${count} new events to the selected ticket.", 
                                        mapping=dict(count=count))
kw['keep_items'] = dict(portal_status_message=portal_status_message,
                        selection_name=selection_name)
return context.Base_redirect(form_id, **kw)
