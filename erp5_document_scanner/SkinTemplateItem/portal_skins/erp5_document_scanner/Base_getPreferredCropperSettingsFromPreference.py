import json

portal = context.getPortalObject()

active_preference = portal.portal_preferences.getActiveUserPreference()
if not active_preference:
  active_preference = portal.portal_preferences.getActivePreference()

canvas_data = active_preference and \
  active_preference.getPreferredCroppedCanvasData() or \
  json.dumps({})
return canvas_data
