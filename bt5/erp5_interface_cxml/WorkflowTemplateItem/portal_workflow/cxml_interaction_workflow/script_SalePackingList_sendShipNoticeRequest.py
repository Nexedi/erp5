return
context = state_change['object']
# only send if object is related to a valid Cxml Order Request
if not context.Base_isCxmlRelated():
  return
# call must  be done in an activity which NEVER retries.
context.activate(
  activity='SQLQueue',
  conflict_retry=False,
  max_retry=0,
).SalePackingList_sendShipNoticeRequest()
