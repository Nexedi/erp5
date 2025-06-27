order_date = context.Order_getRelatedOrderRequestValue().getPropertyDict()['order_date']
assert order_date.Date() == context.getOrderDate().Date()
context.setOrderDate(order_date)
text_content = context.SaleOrder_getConfirmationRequest().encode('utf-8')
connector = context.Base_getCxmlConnectorValueForSale()
# calling sendOutgoingRequest should be done in an activity
# which NEVER retries.
connector.activate(
  activity='SQLQueue',
  conflict_retry=False,
  max_retry=0,
).sendOutgoingRequest(
  text_content,
  portal_type="Cxml Confirmation Request",
  follow_up=context.getRelativeUrl()
)
