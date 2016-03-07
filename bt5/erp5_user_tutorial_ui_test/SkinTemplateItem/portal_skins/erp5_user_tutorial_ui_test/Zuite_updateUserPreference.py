preference_tool = context.getPortalObject().portal_preferences

preference = preference_tool.getActivePreference()

if preference is not None and preference.getPriority() == 3: # XXX: 3 is Priority.USER
  preference.setPreferredTextEditor('text_area')

return 'Init Ok.'
