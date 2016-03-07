related_document_list = []
request = context.REQUEST
document =request.get('current_web_document', context)
isDocument = document.isDocument()
if not isDocument:
  # only document may have relations
  return []

# XXX: make Document_getRelatedDocumentList accept lists (and strings)
for relation_id in relation_id_list:
  related_document_list.extend([x for x in document.Document_getRelatedDocumentList(relation_id=relation_id) \
                                  if x not in related_document_list])
return related_document_list
