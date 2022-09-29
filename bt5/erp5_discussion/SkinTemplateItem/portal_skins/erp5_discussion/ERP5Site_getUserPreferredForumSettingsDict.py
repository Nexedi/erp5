"""
  Get user preference for forum signature..
"""
from Products.ERP5Type.Cache import CachingMethod

portal = context.getPortalObject()

def getPreferredForumSignature(username):
  result = {'preferred_forum_signature': None,
            'preferred_forum_quote_original_message': False}
  preference_list = portal.portal_catalog(
                                       portal_type='Preference',
                                       owner = username,
                                         )
  for preference in preference_list:
    if preference.getPreferenceState() == "enabled":
      result['preferred_forum_signature'] = preference.getPreferredForumSignature()
      result['preferred_forum_quote_original_message'] = preference.getPreferredForumQuoteOriginalMessage()
      break  # user should not have more than 1 enabled preference

  return result

getPreferredForumSignature = CachingMethod(getPreferredForumSignature,
                               ("ERP5Site_getUserPreferredForumSettingsDict", username),
                                cache_factory='erp5_ui_short')
if username is None:
  # assume current logged in user
  result = {'preferred_forum_signature': portal.portal_preferences.getPreferredForumSignature(),
            'preferred_forum_quote_original_message': portal.portal_preferences.getPreferredForumQuoteOriginalMessage()}
else:
  result = getPreferredForumSignature(username)

return result
