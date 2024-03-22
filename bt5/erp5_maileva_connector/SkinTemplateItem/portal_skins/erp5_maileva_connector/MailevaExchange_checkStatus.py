maileva_connector = context.getPortalObject().ERP5Site_getAvailableMailevaSOAPConnector()
result = maileva_connector.getPendingNotificationDetails(track_id)
if result['status'] == "SENT":
  document = context.getFollowUpValue()
  if result['notification_status'] in ("ACCEPT", "OK"):
    document.succeed()
  else:
    document.fail()
  context.acknowledge()

context.edit(
  response_detail = result['detail'],
  track_id = track_id
)
