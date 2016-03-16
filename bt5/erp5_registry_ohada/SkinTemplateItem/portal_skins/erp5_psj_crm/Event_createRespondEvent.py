# this script allows to create a new follow up ticket for a given event
event_object = context
event_module = context.getPortalObject().getDefaultModule(
                                          respond_event_portal_type)
# Create the outgoing
respond_event = event_module.newContent(
                       portal_type=respond_event_portal_type,
                       title=respond_event_title,
                       description=respond_event_description,
                       start_date=DateTime(),
                       source=context.getDefaultDestination(),
                       destination=context.getDefaultSource(),
                       causality=context.getRelativeUrl(),                      
)

if respond_event_quotation:
  respond_event.edit(text_content=context.getReplyBody())
# Change the state to outgoing
respond_event.plan()
