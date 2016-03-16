"""
  This scripts transform used the title of a document
  to produce a pretty reference string optimized for Search Engines.

  Example:
    "New Document - 2006 Edition" -> "new-document-2006-edition"
"""
translateString = context.Base_translateString

title = context.getTitle()
if not title:
  return context.Base_redirect(form_id,
         keep_items = dict(portal_status_message = translateString("Sorry, it is not possible to suggest a reference from an empty title.")), **kw)

nice_uri = ''

for char in title:
  if char.isalnum():
    nice_uri += char.lower()
  elif len(nice_uri) > 0 and nice_uri[-1] != '-':
    nice_uri += '-'

context.setReference(nice_uri)
return context.Base_redirect(form_id,
       keep_items = dict(portal_status_message = translateString("Reference updated.")), **kw)
