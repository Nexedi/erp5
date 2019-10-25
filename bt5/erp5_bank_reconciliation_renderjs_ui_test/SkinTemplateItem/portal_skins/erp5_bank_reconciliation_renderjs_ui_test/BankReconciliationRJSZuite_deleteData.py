portal = context.getPortalObject()

event_portal_type = "Note"
event_id = "erp5_crm_renderjs_ui_test_event"

# Delete event
module = portal.getDefaultModule(event_portal_type)
if getattr(module, event_id, None) is not None:
  module.manage_delObjects([event_id])

notification_message_portal_type = "Notification Message"
notification_message_id = "erp5_crm_renderjs_ui_test_notification"
# Delete Notification Message
module = portal.getDefaultModule(notification_message_portal_type)
if getattr(module, notification_message_id, None) is not None:
  module.manage_delObjects([notification_message_id])

person_portal_type = "Person"
customer_id = "erp5_crm_renderjs_ui_test_customer"
agent_id = "erp5_crm_renderjs_ui_test_agent"

# Delete person
module = portal.getDefaultModule(person_portal_type)
for person_id in (customer_id, agent_id):
  if getattr(module, person_id, None) is not None:
    module.manage_delObjects([person_id])

return "Deleted Successfully."
