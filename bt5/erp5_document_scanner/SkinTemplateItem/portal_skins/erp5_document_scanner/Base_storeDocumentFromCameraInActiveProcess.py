import json
from base64 import decodestring
portal = context.getPortalObject()

translateString = portal.Base_translateString

gadget_data = json.loads(document_scanner_gadget)
image_str = decodestring(gadget_data.pop("input_value"))
preferred_cropped_canvas_data = gadget_data["preferred_cropped_canvas_data"] or {}

portal.portal_selections.setSelectionParamsFor(
  context.Base_getDocumentScannerSelectionName(),
  preferred_cropped_canvas_data,
  context.REQUEST
)

if not image_str:
  if batch_mode:
    if active_process_url:
      return portal.restrictedTraverse(active_process_url)
    return None

  return context.Base_renderForm('Base_viewUploadDocumentFromCameraDialog',
                               message=translateString('Nothing to capture'))

active_process = context.Base_postDataToActiveResult(
  active_process_url,
  image_str)

# We need it to fill the form rendered by renderjs
context.REQUEST.form["your_active_process_url"] = active_process.getRelativeUrl()
# We remove it to reduce the size of the response
context.REQUEST.form.pop("field_your_document_scanner_gadget")
context.REQUEST.form.pop('document_scanner_gadget')

if batch_mode:
  return active_process

return context.Base_renderForm('Base_viewUploadDocumentFromCameraDialog',
                               message=translateString('Captured'))
