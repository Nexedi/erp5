"""
 Return the permanent url for a given document.
 This is based on the reference else we must return the absolute path in current context.
"""
if document.hasReference():
  file_name = document.Document_getStandardFileName()
  return "%s%s" % (context.absolute_url(), file_name)
else:
  return "%s%s" % (document.getAbsoluteUrl(),view and '/view' or '')
