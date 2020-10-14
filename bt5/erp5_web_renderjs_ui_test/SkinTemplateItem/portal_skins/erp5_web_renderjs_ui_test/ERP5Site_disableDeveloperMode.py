portal = context.getPortalObject()
active_preference = portal.portal_preferences.getActivePreference()
if active_preference.getPreferredHtmlStyleDevelopperMode():
  active_preference.setPreferredHtmlStyleDevelopperMode(0)
  active_preference.setPreferredHtmlStyleContextualHelp(0)
  active_preference.setPreferredHtmlStyleTranslatorMode(0)

return "OK"
