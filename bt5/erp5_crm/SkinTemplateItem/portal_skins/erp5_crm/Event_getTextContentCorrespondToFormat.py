from Products.PythonScripts.standard import newline_to_br
from erp5.component.module.Log import log

log("Event_getTextContentCorrespondToFormat is deprecated, use Event_getEditorFieldTextContent instead", level=100) # WARNING

content_type = context.getContentType()

if content_type == 'text/html' and context.hasFile():
  return context.asStrippedHTML()
else:
  value = context.getTextContent()
  if editable:
    return value
  else:
    return newline_to_br(value or "")
