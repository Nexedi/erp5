request = state_change["object"]
portal = request.getPortalObject()
now = DateTime()
request_type = request.getFreeSubscriptionRequestType()
resource = request.getResource()
stop_date = request.getStopDate()

# Rule is we prioritise effective_date if it exists,
# then getStopDate result (stop_date or acquiring from start_date) if it is not None
# and finally current date
if request.hasEffectiveDate():
  effective_date = request.getEffectiveDate()
else:
  effective_date = stop_date or now

free_subscription = request.getFollowUpValue()
if free_subscription is None:
  free_subscription = portal.free_subscription_module.newContent(
    source=request.getSource(),
    destination=request.getDestination(),
    resource=resource,
    effective_date=effective_date,
  )
request.setFollowUpValue(free_subscription)
variation_category_list = request.getVariationCategoryList()

if request_type == "unsubscription":
  assert not variation_category_list, 'unsubscription type of Free Subscription Request with non empty variation_category_list'
  validation_state = free_subscription.getValidationState()
  if validation_state != "invalidated":
    if validation_state == "draft":
      # validate, so that we can invalidate in same transaction
      free_subscription.validate()
    # Rule is we prioritise expiration_date if it exists
    # then getStopDate result (stop_date or acquiring from start_date) if it is not None
    # and finally current date
    if request.hasExpirationDate():
      expiration_date = request.getExpirationDate()
    else:
      expiration_date = stop_date or now
    free_subscription.setExpirationDate(expiration_date)
    free_subscription.invalidate()
elif request_type == "subscription":
  variation_range_category_list = request.getVariationRangeCategoryList()
  if not variation_category_list:
    assert not request.getVariationRangeCategoryList(), 'subscription type of Free Subscription Request with non empty variation_category_list, while resource has list defined'
  for variation_category in variation_category_list:
    assert variation_category in variation_range_category_list, 'not allowed variation_category %s' % variation_category
  free_subscription.setExpirationDate(None)
  if free_subscription.getValidationState() != "validated":
    free_subscription.validate()
    free_subscription.setEffectiveDate(effective_date)
else:
  raise RuntimeError('Unknown request type %s' % request_type)

free_subscription.setVariationCategoryList(variation_category_list)
