"""
  This script creates a new event with given metadata and
  attaches it to the current ticket.
"""
translateString = context.Base_translateString
module = context.getDefaultModule(portal_type)

# Create a new event
event = module.newContent(portal_type=portal_type, description=description, title=title, follow_up=context.getRelativeUrl())

# Trigger appropriate workflow action
if direction == 'incoming':
  event.receive()
else:
  event.plan()

# Redirect to even
portal_status_message = translateString("Created and associated a new ${portal_type} to the ticket.", 
                                    mapping = dict(portal_type = translateString(portal_type)))
event.Base_redirect('view', keep_items = dict(portal_status_message=portal_status_message), **kw)
