request = state_change["object"]

if request.getFreeSubscriptionRequestType() == "unsubscription":
  free_subscription = request.getFollowUpValue()
  if free_subscription.getValidationState() != "invalidated":
    free_subscription.invalidate()
elif request.getFreeSubscriptionRequestType() == "subscription":
  from DateTime import DateTime
  portal = request.getPortalObject()
  free_subscription = portal.free_subscription_module.newContent(
    source=request.getSource(),
    destination=request.getDestination(),
    resource=request.getResource(),
    effective_date=DateTime())
  free_subscription.validate()
  request.setFollowUpValue(free_subscription)
