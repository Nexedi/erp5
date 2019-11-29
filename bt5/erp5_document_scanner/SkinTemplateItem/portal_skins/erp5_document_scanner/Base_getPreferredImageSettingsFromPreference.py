import json

portal = context.getPortalObject()
active_preference = portal.portal_preferences.getActiveUserPreference()
if not active_preference:
  active_preference = portal.portal_preferences.getActivePreference()

setting_dict = {
  "compression": active_preference.getPreferredImageConversionCompression(),
  "enable_greyscale": active_preference.getPreferredImageConversionEnableGreyscale(),
  "brightness": active_preference.getPreferredImageConversionBrightness(),
  "contrast": active_preference.getPreferredImageConversionContrast(),
}

return json.dumps(setting_dict)
