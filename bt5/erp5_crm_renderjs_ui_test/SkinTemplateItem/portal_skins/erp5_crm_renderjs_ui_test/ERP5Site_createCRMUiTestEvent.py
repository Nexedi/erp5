from DateTime import DateTime

portal = context.getPortalObject()

person_portal_type = "Person"
customer_id = "erp5_crm_renderjs_ui_test_customer"
customer_title = "erp5_crm_renderjs_ui_test_customer_title"
agent_id = "erp5_crm_renderjs_ui_test_agent"
agent_title = "erp5_crm_renderjs_ui_test_agent_title"

module = portal.getDefaultModule(person_portal_type)
customer = module.newContent(
  portal_type=person_portal_type,
  id=customer_id,
  title=customer_title
)
agent = module.newContent(
  portal_type=person_portal_type,
  id=agent_id,
  title=agent_title
)

notification_message_portal_type = "Notification Message"
notification_message_id = "erp5_crm_renderjs_ui_test_notification"
notification_message_title = "erp5_crm_renderjs_ui_test_notification_title"
notification_message_reference = "erp5_crm_renderjs_ui_test_notification_reference"
notification_message_text_content = """No pbl.
We will solve your issue.
"""

module = portal.getDefaultModule(notification_message_portal_type)
notification_message = module.newContent(
  portal_type=notification_message_portal_type,
  id=notification_message_id,
  title=notification_message_title,
  reference=notification_message_reference,
  text_content=notification_message_text_content
)
notification_message.validate()

event_portal_type = "Note"
event_id = "erp5_crm_renderjs_ui_test_event"
event_title = "erp5_crm_renderjs_ui_test_event_title"
event_text_content = """Hello,
I have an issue
"""

module = portal.getDefaultModule(event_portal_type)
event = module.newContent(
  portal_type=event_portal_type,
  id=event_id,
  title=event_title,
  text_content=event_text_content,
  source_value=customer,
  destination_value=agent,
)
portal.portal_workflow.doActionFor(event, 'initial_stop_action')

return "Event Created."
