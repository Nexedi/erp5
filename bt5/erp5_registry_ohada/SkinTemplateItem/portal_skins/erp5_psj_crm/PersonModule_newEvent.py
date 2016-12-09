"""
  This script creates a new event with given metadata and
  attaches it to the current ticket.
"""
translateString = context.Base_translateString
module = context.getDefaultModule(portal_type)

# Build selection
person_list = context.portal_selections.getSelectionCheckedValueList(selection_name)
if not person_list:
  person_list = context.portal_selections.getSelectionValueList(selection_name)

# Find authenticated user
user_value = context.portal_membership.getAuthenticatedMember().getUserValue()

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
      event.setSourceValue(person)
      event.setDestinationValue(user_value)
      event.receive()
    else:
      event.plan()
      event.setDestinationValue(person)
      event.setSourceValue(user_value)
else:
  if direction == 'incoming' and len(person_list) > 1:
    # This case is not possible
    portal_status_message = translateString("The Single Event option can only be used with outgoing messages",
                                    mapping = dict(portal_type = portal_type, count=count))
    return context.Base_redirect(form_id, keep_items = dict(portal_status_message=portal_status_message, selection_name=selection_name, selection_index=selection_index), **kw)
  # Proceed to event creation
  event = module.newContent(portal_type=portal_type, 
                            description=description, 
                            title=title, 
                            follow_up=follow_up,
                            text_content=text_content) # text_format is set by Event_init
  event.plan()
  event.setDestinationValueList(person_list)
  event.setSourceValue(user_value)
  count = 1

# Redirect to the event module (but is this the best place to go since events are not yet indexed ?)
portal_status_message = translateString("Created and associated ${count} new ${portal_type}(s) to the selected ticket.", 
                                    mapping = dict(portal_type = portal_type, count=count))
context.Base_redirect(form_id, keep_items = dict(portal_status_message=portal_status_message, selection_name=selection_name, selection_index=selection_index), **kw)
