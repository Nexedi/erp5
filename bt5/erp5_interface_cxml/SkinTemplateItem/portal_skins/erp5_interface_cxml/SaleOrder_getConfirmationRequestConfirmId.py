connector = context.Base_getCxmlConnectorValueForSale()
return connector.getPayloadId().split('@')[0]
# if we get a new version of the order we always use "new" operation even
# if we already sent an order confirmation
#if context.getSimulationState() != "confirmed" and str(context.getVersion()) != "1":
#  return "new"
# firs try to find a previous successfull Confirmation Request and retun its confirm id
document_list = context.getFollowUpRelatedValueList(portal_type="Cxml Confirmation Request")
for start_date, cxml_document in reversed(sorted([(x.getStartDate(), x) for x in document_list])):
  if cxml_document.getDocumentType() == "ConfirmationRequest":
    response = cxml_document.getSuccessorValue()
    if response is not None:
      # Check if the response to the ShipNoticeRequest has a
      # a status code 2xx. Only then we had a successfull
      # ShipNoticeRequest before and the next ShipNoticeRequest
      # is an update
      if response.getStatusCode().startswith("2"):
        return cxml_document.getConfirmId()
# we send a Confirmation Request with type "new", so generate a new confirmId
connector = context.Base_getCxmlConnectorValueForSale()
return connector.getPayloadId().split('@')[0]
