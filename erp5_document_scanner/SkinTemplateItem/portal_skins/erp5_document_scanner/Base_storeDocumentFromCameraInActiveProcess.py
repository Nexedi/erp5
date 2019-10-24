import json
from base64 import decodestring
portal = context.getPortalObject()

gadget_data = json.loads(document_scanner_gadget)
image_str = decodestring(gadget_data.pop("input_value"))
preferred_cropped_canvas_data = json.dumps(gadget_data["preferred_cropped_canvas_data"])

active_preference = portal.portal_preferences.getActiveUserPreference()
if not active_preference:
  active_preference = portal.portal_preferences.getActivePreference()

if active_preference and preferred_cropped_canvas_data:
  active_preference.setPreferredCroppedCanvasData(preferred_cropped_canvas_data)

if active_process_url:
  active_process = portal.restrictedTraverse(active_process_url)

if not image_str:
  if batch_mode:
    return active_process

  return context.Base_renderForm('Base_viewUploadDocumentFromCameraDialog',
                               message='Nothing to capture')

if not active_process_url:
  active_process = portal.portal_activities.newActiveProcess()
  context.REQUEST.form["your_active_process_url"] = active_process.getRelativeUrl()

active_process.postActiveResult(detail=image_str)
context.REQUEST.form.pop("field_your_document_scanner_gadget")
context.REQUEST.form.pop('document_scanner_gadget')

if batch_mode:
  return active_process

return context.Base_renderForm('Base_viewUploadDocumentFromCameraDialog',
                               message='Captured')
