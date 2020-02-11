import json

portal = context.getPortalObject()
active_preference = portal.portal_preferences.getActiveUserPreference()
if not active_preference:
  active_preference = portal.portal_preferences.getActivePreference()

setting_dict = {
  "compression": active_preference.getPreferredImageScannerConversionCompression(),
  "enable_greyscale": active_preference.getPreferredImageScannerConversionEnableGreyscale(),
  "brightness": active_preference.getPreferredImageScannerConversionBrightness(),
  "contrast": active_preference.getPreferredImageScannerConversionContrast(),
}

return json.dumps(setting_dict)
