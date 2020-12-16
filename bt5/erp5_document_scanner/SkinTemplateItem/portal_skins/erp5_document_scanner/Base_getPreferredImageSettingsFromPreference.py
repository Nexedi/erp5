import json

preference_tool = context.getPortalObject().portal_preferences

setting_dict = {
  "compression": preference_tool.getPreferredImageScannerConversionCompression(),
  "enable_greyscale": preference_tool.getPreferredImageScannerConversionEnableGreyscale(),
  "brightness": preference_tool.getPreferredImageScannerConversionBrightness(),
  "contrast": preference_tool.getPreferredImageScannerConversionContrast(),
  "maximum_width": preference_tool.getPreferredImageScannerConversionMaximumWidth()
}

return json.dumps(setting_dict)
