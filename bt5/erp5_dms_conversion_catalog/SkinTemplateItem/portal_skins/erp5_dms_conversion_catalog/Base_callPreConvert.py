"""
  Pre convert to know good defaults.
  Use type based methods to allow finer granularity (for example in case of PDF we support many frames inside a document).
"""
portal = context.getPortalObject()

if not context.Base_isConvertible():
  # no need to convert any non convertible types
  return

if kw=={}:
  # use default set of system preferences
  format = portal.portal_preferences.getPreferredImageFormat()
  quality = portal.portal_preferences.getPreferredImageQuality()
  # thumbnail is required always
  display_list = ["thumbnail"]
  kw = dict(format=format, quality=quality, display_list = display_list)

method = context.getTypeBasedMethod('preConvert')
return method(**kw)
