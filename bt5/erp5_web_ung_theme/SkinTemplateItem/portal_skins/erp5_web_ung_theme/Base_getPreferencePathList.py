from json import dumps

if context.portal_membership.isAnonymousUser():
  return dumps(None)

portal_preferences = context.portal_preferences
preference = portal_preferences.getActiveUserPreference()

preference_dict = {}

if preference:
  preference_dict["preference"] = preference.getRelativeUrl()

return dumps(preference_dict)
