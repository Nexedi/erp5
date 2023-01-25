"""
    Determine whether the document being viewed is a web page or the default
    page of a web section. If it is, related discussions can be displayed
"""
document = context
portal_type = document.getPortalType()

if portal_type == 'Web Page':
  return context.getReference()

if portal_type == 'Web Section':
  default_page = document.getAggregate()
  if default_page is not None:
    default_page_document = context.restrictedTraverse(default_page)
    return default_page_document.getReference()

return None
