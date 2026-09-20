portal = context.getPortalObject()
maileva_connector_path = portal.ERP5Site_getAvailableMailevaSOAPConnector()
maileva_connector = portal.restrictTraverse(maileva_connector_path)

notification_dict = maileva_connector.checkPendingNotifications()

for event in portal.portal_catalog(
  portal_type="Maileva Exchange",
  validation_state="confirmed"
):
  if event.getReference() in notification_dict:
    event.activate(tag=tag).MailevaExchange_checkStatus(track_id=notification_dict[event.getReference()]["id"])
  elif getattr(event, 'track_id', ""):
    event.activate(tag=tag).MailevaExchange_checkStatus(track_id=getattr(event, 'track_id'))
  else:
    document = event.getFollowUpValue()
    send_state = document.getSendState()
    if send_state == "failed":
      event.acknowledge(comment="Document failed to send")
    else:
      if DateTime() - event.getCreationDate() > 1:
        document.fail()
        event.acknowledge(comment="No Response")

context.activate(after_tag=tag).getId()
