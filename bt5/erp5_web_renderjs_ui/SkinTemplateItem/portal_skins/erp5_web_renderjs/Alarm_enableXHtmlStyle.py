portal = context.getPortalObject()
portal_preferences = portal.portal_preferences

if portal_preferences.isPreferredHtmlStyleDisabled():

  system_preference = portal_preferences.getActiveSystemPreference()
  if system_preference is None:
    system_preference = portal_preferences.newContent(
                   portal_type="System Preference",
                   title="Created by Alarm",
                   activate_kw={'tag': tag})
    system_preference.enable()

  system_preference.edit(
    preferred_html_style_disabled=False
  )

context.activate(after_tag=tag).getId()
