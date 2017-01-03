request = context.REQUEST
response = request.RESPONSE
context.Base_prepareCorsResponse(RESPONSE=response)
content_type = context.getContentType()
if  (not content_type) or content_type.startswith("application/x-asc-"):
  return context.index_html(request, response, format=None, inline=inline)
if context.getExternalProcessingState() == "converted":
  return context.index_html(request, response, format="html", inline=inline)
return "No Data available (maybe wrong format or not ready yet)"
