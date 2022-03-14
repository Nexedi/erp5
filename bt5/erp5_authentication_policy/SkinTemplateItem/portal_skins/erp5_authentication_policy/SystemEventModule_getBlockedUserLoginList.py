"""
  Return list of blocked user logins in a 'listbox' format
"""
from DateTime import DateTime
from Products.ZSQLCatalog.SQLCatalog import Query
from Products.ERP5Type.Document import newTempBase

portal = context.getPortalObject()
portal_preferences = portal.portal_preferences

blocked_user_login_list = []
all_blocked_user_login_dict = {}

now = DateTime()
one_second = 1/24.0/60.0/60.0
check_duration = portal_preferences.getPreferredAuthenticationFailureCheckDuration()
max_authentication_failures = portal_preferences.getPreferredMaxAuthenticationFailure()
check_time = now - check_duration*one_second

kw = {'portal_type': 'Authentication Event',
      'creation_date': Query(creation_date = check_time,
                             range='min'),
      'validation_state' : 'confirmed'}
failure_list = portal.portal_catalog(**kw)
for failure in failure_list:
  login = failure.getDestinationValue()
  if login not in list(all_blocked_user_login_dict.keys()):
    all_blocked_user_login_dict[login] = []
  all_blocked_user_login_dict[login].append(failure)

# leave only ones that are blocked:
for login, failure_list in list(all_blocked_user_login_dict.items()):
  if len(failure_list) >= max_authentication_failures:
    person = login.getParentValue()
    blocked_user_login_list.append(newTempBase(portal,
                                               person.getTitle(),
                                               **{'title': person.getTitle(),
                                                  'count':len(failure_list),
                                                  'reference': login.getReference(),
                                                  'url': login.absolute_url()}))
return blocked_user_login_list
