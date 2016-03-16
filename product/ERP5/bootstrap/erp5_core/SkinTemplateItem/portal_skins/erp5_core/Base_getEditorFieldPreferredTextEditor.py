"""Returns the preferred text editor and tries to take into account a default
content type if any.
The content type can also be passed, for example to use the editor in a dialog
that will create a document of this target content type.
"""
if not content_type:
  # By default, everthing related to EditorField is HTML
  content_type = 'text/html'
  
  # If this document has a content type we use this information
  if getattr(context, 'getContentType', None) is not None:
    content_type = context.getContentType() or 'text/html'

# If this is HTML, use preferred HTML editor or fallback to Textarea
if content_type == 'text/html':
  return context.portal_preferences.getPreferredTextEditor() or 'text_area'

# Else use preferred source code editor or fallback to Textarea
return context.portal_preferences.getPreferredSourceCodeEditor() or 'text_area'
