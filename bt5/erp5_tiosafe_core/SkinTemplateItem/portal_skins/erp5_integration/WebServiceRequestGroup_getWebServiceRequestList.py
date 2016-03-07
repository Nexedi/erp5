result = []
for web_service_request in context.getParentValue().contentValues(
    portal_type='Web Service Request'):
  result.append(web_service_request.getId())

return result
