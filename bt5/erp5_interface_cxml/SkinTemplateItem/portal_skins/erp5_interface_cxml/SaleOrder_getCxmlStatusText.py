document_list = context.getFollowUpRelatedValueList(portal_type="Cxml Confirmation Request")
for start_date, cxml_document in reversed(sorted([(x.getStartDate(), x) for x in document_list])):
  if cxml_document.getDocumentType() == "ConfirmationRequest":
    response = cxml_document.getSuccessorValue()
    if response is not None:
      # Check if the response to the ShipNoticeRequest has a
      # a status code 2xx. Only then we had a successfull
      # ConfirmationRequest
      if response.getStatusCode().startswith("2"):
        return "Confirmation accepted"
      return "Confirmation not accepted"
    return "Confirmation sent but no reply"
return "Confirmation not sent"
