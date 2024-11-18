context = state_change['object']
# only send OrderConfirmationRequest if the Sale Order
# is related to a valid Cxml Order Request and if it is not the first version
# of the order
if not context.Base_isCxmlRelated(): #or str(context.getVersion()) != "1":
  return
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
