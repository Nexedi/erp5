request = context.REQUEST
return request.RESPONSE.redirect( "%s/Preference_viewAccounting" %
  context.portal_preferences.getActivePreference().absolute_url())

# vim: syntax=python
