# type: () -> Optional[erp5.portal_type.WebScript]
"""Returns the web script used to contain the translation data for this RJS web site.
"""

translation_gadget_url = context.getLayoutProperty(
    "configuration_translation_gadget_url")
if not translation_gadget_url:
  return None
translation_gadget = context.getDocumentValue(translation_gadget_url)
if not translation_gadget:
  return None

# find the .js containing translation data
for successor in translation_gadget.getImplicitSuccessorValueList():
  successor = successor.getObject()
  if successor.getReference() and successor.getReference().endswith(
      'translation_data.js'):
    return successor

return None
