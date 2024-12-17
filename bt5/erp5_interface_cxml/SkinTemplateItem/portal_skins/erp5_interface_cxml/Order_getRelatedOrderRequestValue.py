portal_type = context.getPortalType()
order = None
if portal_type == "Sale Order":
  order = context
elif portal_type in ("Sale Packing List", "Sale Invoice Transaction"):
  order = context.getCausalityValue(portal_type="Sale Order")
if order is not None:
  for order_request in order.getFollowUpRelatedValueList(portal_type="Cxml Order Request"):
    if order_request.getValidationState() == 'validated':
      return order_request
