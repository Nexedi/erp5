import json

active_process = context.getPortalObject().portal_activities.newActiveProcess()

return json.dumps({
  "active_process": active_process.getRelativeUrl(),
  "image_list": []
})
