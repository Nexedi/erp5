"""
  A core method that will return default image conversion arguments as a dict.
"""
portal = context.getPortalObject()
portal_preferences = portal.portal_preferences
image_argument_dict = {'format': portal_preferences.getPreferredImageFormat(),
                       'quality': portal_preferences.getPreferredImageQuality()}

pre_converted_only = portal_preferences.getPreferredPreConvertedOnly()
if pre_converted_only:
  # only add if it's True as conversion machine assume that if it is missing
  # then conversion should happen "on the fly"
  image_argument_dict['pre_converted_only'] = pre_converted_only

if context.getPortalType() in ('PDF',):
  # PDF support frames
  image_argument_dict['frame'] = 0
return image_argument_dict
