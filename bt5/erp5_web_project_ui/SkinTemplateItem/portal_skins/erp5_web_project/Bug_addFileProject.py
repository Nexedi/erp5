"""
  Adds the uploaded file to the bug with the forge Bug_newFile, then goes back to the bug,
  or to the bug line it created, which the bug messages only list once indexed.
"""
# this script has a `file` argument
# pylint: disable=redefined-builtin
if not file:
  raise ValueError('No file uploaded')

content_type = file.headers.get('Content-Type') or ''
portal_type = 'Image' if content_type.startswith('image/') else 'File'
is_new_bug_line = not context.hasContent('default_bug_line')
context.Bug_newFile(portal_type=portal_type,
                    title=file.filename,
                    description=description,
                    file=file)

portal_status_message = context.Base_translateString(
  "New ${portal_type} added.",
  mapping=dict(portal_type=context.Base_translateString(portal_type)))
kw['keep_items'] = dict(portal_status_message=portal_status_message)
redirect_document = context.default_bug_line if is_new_bug_line else context
return redirect_document.Base_redirect('view', **kw)
