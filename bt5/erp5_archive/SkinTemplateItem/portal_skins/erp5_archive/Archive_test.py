non_reflected_portal_type = []
item_container_type_list = []

log = 0
result = True

if log:
  context.log("object = %s" %(context,), "archive = %s" %(predicate,))

# items and their container go in all catalog
ptype = context.getPortalType()
if context.isItemType():
  return True
if ptype in item_container_type_list:
  return True

if getattr(context, 'getExplanationValue', None) is not None:
  try:
    explanation_value = context.getExplanationValue()
  except AttributeError:
    context.log("Archive_test, getExplanationValue failed", "obj = %s" %(context,))
    explanation_value = None
  if explanation_value is not None and explanation_value.getPortalType() \
         in item_container_type_list:
    return True

# Except those we don't want
if ptype not in non_reflected_portal_type:
  # Object not delivery or movement goes in all archive
  if not(context.providesIMovement() or context.isDelivery()):
    if log:
      context.log(" - document is not Movement/Delivery", "")
    return True
else:
  result = result and True
  if log:
    context.log(" - result after reflected", "%s" %result)

# Check Date
if getattr(context, 'getStopDate', None) is not None:
  max_stop_date = predicate.getStopDateRangeMax()
  min_stop_date = predicate.getStopDateRangeMin()
  if log:
    context.log("obj stop date %s" %context.getStopDate(), "min %s, max %s" %(min_stop_date, max_stop_date))
  if max_stop_date is not None:
    result = result and (context.getStopDate() < max_stop_date)
  if min_stop_date is not None:
    result = result and (context.getStopDate() >= min_stop_date)
if log:
  context.log("result after date", result)


# XXX must manage specific case like Applied Rule, where do we want them to go ?
return result
