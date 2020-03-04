import json

active_process = context.getPortalObject().portal_activities.newActiveProcess(
  reference=context.Base_getDocumentScannerDefaultReference())

return json.dumps({
  "active_process": active_process.getRelativeUrl(),
  "image_list": []
})
