document_list = context.getFollowUpRelatedValueList(portal_type="Cxml Document")
for start_date, cxml_document in reversed(sorted([(x.getStartDate(), x) for x in document_list])):
  if cxml_document.getDocumentType() == "ShipNoticeRequest":
    response = cxml_document.getSuccessorValue()
    if response is not None:
      # Check if the response to the ShipNoticeRequest has a
      # a status code 2xx. Only then we had a successfull
      # ConfirmationRequest
      if response.getStatusCode().startswith("2"):
        return "ASN accepted"
      return "ASN not accepted"
    return "ASN sent but no reply"
return "ASN not sent"
