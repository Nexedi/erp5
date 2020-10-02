"""
 TODO: This script does not work now. This needs proxy role, but if proxified, then this script can be a security hole.
       Because anyone can create an email and send to everywhere. (Yusei)
"""

# this script allows to create a new follow up ticket for a given event
event_module = context.getPortalObject().getDefaultModule(respond_event_portal_type)
# Create the outgoing
respond_event = event_module.newContent(
      portal_type=respond_event_portal_type,
      title=respond_event_title,
      resource=respond_event_resource,
      start_date=DateTime(),
      source=context.getDefaultDestination(),
      destination=context.getDefaultSource(),
      causality=context.getRelativeUrl(),
      follow_up=context.getFollowUp(),
      text_content=respond_event_text_content,
      content_type=context.getContentType()
      )

# Change the state to posted
respond_event.start()

if respond_event.portal_type=='Mail Message' and respond_event.getSource():
  respond_event.send()
else:
  respond_event.send(from_url=context.portal_preferences.getPreferredEventSenderEmail())
