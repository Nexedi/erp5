import json

portal = context.getPortalObject()

active_preference = portal.portal_preferences.getActiveUserPreference()
if not active_preference:
  active_preference = portal.portal_preferences.getActivePreference()

canvas_data = active_preference and \
  json.loads(active_preference.getPreferredCroppedCanvasData("{}")) or {}

canvas_data["dialog_method"] = context.Base_storeDocumentFromCameraInActiveProcess.getId()

return json.dumps(canvas_data)
