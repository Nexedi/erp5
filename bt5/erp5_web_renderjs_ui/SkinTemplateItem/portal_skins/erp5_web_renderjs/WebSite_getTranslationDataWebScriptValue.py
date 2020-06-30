# type: () -> Optional[erp5.portal_type.WebScript]
"""Returns the web script used to contain the translation data for this RJS web site.
"""

# OfficeJS is a bit more complex, the translation gadget is defined on the
# `app` web section, which is defined in "configuration_latest_version"
officejs_latest_version = context.getLayoutProperty(
    "configuration_latest_version")
if officejs_latest_version:
  if officejs_latest_version.endswith('/'):
    officejs_latest_version = officejs_latest_version[:-1]
  context = context.restrictedTraverse(officejs_latest_version, None)
  if context is None:
    return None
  # now `context` is the app web section and the logic is same as with a normal
  # ERP5JS web site.

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
