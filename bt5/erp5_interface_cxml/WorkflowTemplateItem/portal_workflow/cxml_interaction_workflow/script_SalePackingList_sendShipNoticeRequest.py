context = state_change['object']
# only send ShipNoticeRequest if the Sale Packing List is related to
# a Sale Order which is related to a valid Cxml Order Request
if not context.Base_isCxmlRelated():
  return
text_content = context.SalePackingList_getShipNoticeRequest().encode('utf-8')
connector = context.Base_getCxmlConnectorValueForSale()
# calling sendOutgoingRequest should be done in an activity
# which NEVER retries.
connector.activate(
  activity='SQLQueue',
  conflict_retry=False,
  max_retry=0,
).sendOutgoingRequest(text_content, follow_up=context.getRelativeUrl())
