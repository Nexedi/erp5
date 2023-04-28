"""
  Do actual conversion of OOo types.
"""
portal = context.getPortalObject()

if context.hasBaseData():
  if quality is None:
    quality = portal.portal_preferences.getPreferredImageQuality()

  # empty documents do not need pre conversion
  context.activate(activity='SQLDict', serialization_tag='pre_convert').convert(**{'format': 'html'})
  context.activate(activity='SQLDict', serialization_tag='pre_convert').Base_preConvert(format, quality, display_list)
