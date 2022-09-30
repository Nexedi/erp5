"""
  This script redirects the current user to its
  active preference. If a user has no preference
  yet, then it creates a new preference and redirects
  to it. In case a failure, a message is displayed.
"""
from zExceptions import Unauthorized

# Initialize some useful variables
portal = context.getPortalObject()
user = portal.portal_membership.getAuthenticatedMember()
user_preference = None
portal_preferences = portal.portal_preferences

# Find user owned preferences
kw = {'portal_type': 'Preference',
      'owner': user}
user_preference_list = portal_preferences.searchFolder(**kw)

if not len(user_preference_list):
  # create and enable a user owned preference
  # if no preference exists
  try:
    user_preference = portal_preferences.newContent(
                                         portal_type='Preference',
                                         title='Preference for %s' %user)
    user_preference.enable()
  except Unauthorized:
    # user is not allowed to have its own preference
    user_preference = None
else:
  user_active_preference_list = portal_preferences.searchFolder(
                                preference_state='active', **kw)
  if len(user_active_preference_list):
    # try to find an active preference
    user_preference = user_active_preference_list[0]
  else:
    # if not use the first non active
    user_preference = user_preference_list[0]

# make sure next view is returned again into the context of the web site itself
if user_preference is None:
  translateString = context.Base_translateString
  msg = translateString("Could not create user preferences.")
  return context.Base_redirect(form_id="view", keep_items={'portal_status_message':msg})
else:
  return user_preference.Base_redirect(form_id="view", keep_items={'editable_mode':1})
