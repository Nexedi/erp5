portal = context.getPortalObject()
if portal.Base_getHMACHexdigest(portal.Base_getEventHMACKey(), event_id) != hmac:
  from zExceptions import Unauthorized
  raise Unauthorized

event = portal.event_module[event_id]

# First create a request
request = portal.free_subscription_request_module.newContent(
  source=event.getSource(),
  destination=event.getDestination(),
  resource = event.getResource(),
  free_subscription_request_type="unsubscription",
  causality_value=event,
  )

free_subscription_list = portal.portal_catalog(portal_type="Free Subscription",
  default_resource_uid=event.getResourceUid(),
  default_source_uid=event.getSourceUid(),
  default_destination_uid=event.getDestinationUid())

if len(free_subscription_list) != 1:
  raise ValueError("Impossible to find the free subscription (%d)" %
    (len(free_subscription_list)))
free_subscription = free_subscription_list[0].getObject()
request.setFollowUpValue(free_subscription)

request.submit()
