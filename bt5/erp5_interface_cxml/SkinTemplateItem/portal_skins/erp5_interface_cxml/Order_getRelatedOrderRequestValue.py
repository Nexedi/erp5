portal_type = context.getPortalType()
order = None
if portal_type == "Sale Order":
  order = context
elif portal_type in ("Sale Packing List", "Sale Invoice Transaction"):
  order = context.getCausalityValue(portal_type="Sale Order")
if order is not None:
  for order_request in order.getFollowUpRelatedValueList(portal_type="Cxml Order Request"):
    if order_request.getValidationState() == 'validated' and order_request.getVersion() == order.getVersion():
      return order_request
  current_version = 0
  current_order_request = None
  for order_request in order.getFollowUpRelatedValueList(portal_type="Cxml Order Request"):
    if order_request.getValidationState() == 'validated' and order_request.getVersion() > current_version:
      current_version = order_request.getVersion()
      current_order_request = order_request
  return current_order_request
