portal = context.getPortalObject()
container = portal.system_event_module
if object_id is not None and object_id in container:
  return
http_exchange = container.newContent(
  id=object_id,
  portal_type='HTTP Exchange',
  request=request,
  response=response,
  resource_value=None if notification_type is None else getattr(portal.portal_categories.http_exchange_resource.payline.notification, notification_type),
  source_value=context,
)
# Trigger the alarm before changing the event state
# (and so, removing the access permission)
http_exchange.Base_reindexAndSenseAlarm(['handle_confirmed_http_exchanges'])
# Notification ends in confirmed state, to be picked up by alarm (for security context switch)
http_exchange.confirm()
