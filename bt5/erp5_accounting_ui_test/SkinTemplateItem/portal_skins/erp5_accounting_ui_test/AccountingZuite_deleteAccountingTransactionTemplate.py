preference = context.portal_preferences.getActivePreference()
preference.manage_delObjects(ids=[temp.getId() for temp in preference.Preference_getTemplateList()])

return 'Done.'
