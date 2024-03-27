portal = context.getPortalObject()
maileva_connector = portal.ERP5Site_getAvailableMailevaSOAPConnector()

notification_dict = maileva_connector.checkPendingNotifications()

for event in portal.portal_catalog(
  portal_type="Maileva Exchange",
  validation_state="confirmed"
):
  if event.getReference() in notification_dict:
    event.activate().MailevaExchange_checkStatus(track_id= notification_dict[event.getReference()]["id"])
  elif getattr(event, 'track_id', ""):
    event.activate().MailevaExchange_checkStatus(track_id= getattr(event, 'track_id'))
  else:
    if int(DateTime()) - int(event.getCreationDate()) > 60*60*24:
      document = event.getFollowUpValue()
      document.fail()
      event.acknowledge(comment="No Response")

context.activate(after_tag=tag).getId()
