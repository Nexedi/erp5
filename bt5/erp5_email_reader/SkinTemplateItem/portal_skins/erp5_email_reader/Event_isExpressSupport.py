email = 'express-support@tiolive.com'

destination_list = context.getDestinationValueList() or []
source_list = context.getSourceValueList() or []

document_list = destination_list + source_list

for document in document_list:
  if document.getDefaultEmailText()==email:
    return True

return False
