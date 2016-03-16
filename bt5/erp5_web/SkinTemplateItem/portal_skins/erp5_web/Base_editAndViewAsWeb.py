# Retrieve the edit action
"""
  Special edit method which returns to view mode.
  The view_document_url is used to define the URL to return to
  after editing the document.
"""

# This is required in case of field using 'is_web_mode' in TALES expression
context.REQUEST.set('is_web_mode', 1)

# Retrieve the edit action
edit_method = getattr(context, form_action)
return edit_method(form_id, editable_mode=0, ignore_layout=ignore_layout, **kw)
