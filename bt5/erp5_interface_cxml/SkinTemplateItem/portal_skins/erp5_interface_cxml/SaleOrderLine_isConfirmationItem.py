sale_order = context.getParentValue()
# if the line was in the previous order confirmation and it did not
# change, then it is not included in the new confirmation request
document_list = sale_order.getFollowUpRelatedValueList(portal_type="Cxml Confirmation Request")
for start_date, cxml_document in reversed(sorted([(x.getStartDate(), x) for x in document_list])):
  if cxml_document.getDocumentType() == "ConfirmationRequest":
    response = cxml_document.getSuccessorValue()
    if response is not None:
      # Check if the response to the ShipNoticeRequest has a
      # a status code 2xx. Only then we had a successfull
      # ShipNoticeRequest before and the next ShipNoticeRequest
      # is an update
      if response.getStatusCode().startswith("2"):
        previous_confirmation_request = cxml_document
        break
else:
  # no previous confirmation request found, so we include the line
  return True

int_index = context.getIntIndex()
property_dict = previous_confirmation_request.getLinePropertyDict().get(int_index)
if property_dict is None:
  return True
property_tuple = "quantity", "start_date", "stop_date"
for property_id in property_tuple:
  if property_dict.get(property_id) != context.getProperty(property_id):
    # a property is different, so we include the line
    return True
# all properties are the same, so we do not include the line
return False
