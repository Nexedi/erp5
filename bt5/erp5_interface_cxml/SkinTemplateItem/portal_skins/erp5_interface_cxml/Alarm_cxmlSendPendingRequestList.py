portal = context.getPortalObject()

# In the periodic pending request we us an old
# date to not remove messages from the queue.
# Only after downloading a message we set
# the timestamp from the response to empty the queue
old_time_stamp = "2024-04-05T14:15:09-07:00"
message_type_list = ('OrderRequest',)
connector = portal.ERP5Site_getCxmlConnectorValue()
if connector is None:
  return
for message_type in message_type_list:
  connector.sendGetPendingRequest(
    message_type=message_type,
    last_received_timestamp=old_time_stamp
  )
