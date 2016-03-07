document_value_list = context.getDocumentValueList(*args, **kw)
context.REQUEST.set('cached_document_value_list', document_value_list)
return document_value_list
