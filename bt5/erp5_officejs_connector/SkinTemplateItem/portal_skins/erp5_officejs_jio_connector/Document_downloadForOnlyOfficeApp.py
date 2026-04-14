request = context.REQUEST
response = request.RESPONSE
context.Base_prepareCorsResponse(RESPONSE=response)
content_type = context.getContentType()
if  (not content_type) or content_type.startswith("application/x-asc-"):
  return context.index_html(request, response, format=None, inline=inline)

return context.index_html(request, response, format="html", inline=inline)
