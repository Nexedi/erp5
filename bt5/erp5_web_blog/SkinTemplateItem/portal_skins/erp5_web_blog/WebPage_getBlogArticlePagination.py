# call web section's render to get document value list.
context.getWebSectionValue().WebSection_viewBlogFrontPage()

document_value_list = context.REQUEST.get('cached_document_value_list', [])
prev = None
next = None
if document_value_list:
  reference_list = [x.reference for x in document_value_list]
  try:
    i = reference_list.index(context.getReference())
  except ValueError:
    i = 0
  if i - 1 >= 0:
    prev = document_value_list[i - 1]
  if i + 1 < len(reference_list):
    next = document_value_list[i + 1]
return prev, next
