# Manager Role, to be able to create Active Process
from zExceptions import Unauthorized
import json

if REQUEST is not None:
  raise Unauthorized
active_process = context.getPortalObject().portal_activities.newActiveProcess(
  reference=context.Base_getDocumentScannerDefaultReference())

return json.dumps({
  "active_process": active_process.getRelativeUrl(),
  "image_list": []
})
