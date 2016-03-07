"""
  Returns the HTML content which must be displayed by the Editor Field.

  Unlike other fields (which should never try to generate HTML), Editor
  Field expects to be provided valid HTML. It is therefore the responsibility
  of the Default value script to provide this valid HTML.
"""
# Define default editable value
if editable is None:
  editable = context.Event_isTextContentEditable()

# If content is editable, nothing to do
if editable:
  return context.getTextContent()

# If not, convert it to stripped HTML (read-only)
return context.asStrippedHTML()
