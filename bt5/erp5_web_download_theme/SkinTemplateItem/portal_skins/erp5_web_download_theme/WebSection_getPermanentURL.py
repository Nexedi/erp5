"""
 Return the permanent url for a given document.
 This is based on the reference else we must return the absolute path in current context.
"""
if document.hasReference():
  file_name = document.Document_getStandardFileName()
  return context.constructUrlFor(document_reference=file_name)
else:
  return context.constructUrlFor(form_id='view' if view else None)
