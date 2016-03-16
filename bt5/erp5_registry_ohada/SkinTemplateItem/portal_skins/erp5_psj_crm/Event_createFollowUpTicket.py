# this script allows to create a new follow up ticket for a given event
event = context
ticket_module = event.getPortalObject().getDefaultModule(follow_up_ticket_type)

# Create a new object
new_object = ticket_module.newContent(
     portal_type=follow_up_ticket_type,
     title=follow_up_ticket_title,
     destination_decision_list=event.getSourceList()
)

# Now create the relation between the event object and the new follow up ticket
event.setFollowUpValueList([new_object])
