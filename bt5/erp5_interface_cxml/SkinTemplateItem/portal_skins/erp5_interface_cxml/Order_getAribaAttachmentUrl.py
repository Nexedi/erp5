order_request = context.Order_getRelatedOrderRequestValue()
if order_request is not None:
  return order_request.getAribaAttachmentUrl()
return ''
