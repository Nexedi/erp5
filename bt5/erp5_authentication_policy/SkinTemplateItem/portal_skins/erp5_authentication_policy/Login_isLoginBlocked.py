"""
  Return true if user account is blocked.
"""
from DateTime import DateTime
from Products.ZSQLCatalog.SQLCatalog import Query
from erp5.component.module.Log import log

request = context.REQUEST
portal = context.getPortalObject()
portal_preferences = portal.portal_preferences

if not portal_preferences.isAuthenticationPolicyEnabled():
  # no policy, no sense to block account
  return 0

now = DateTime()
one_second = 1/24.0/60.0/60.0
check_duration = portal_preferences.getPreferredAuthenticationFailureCheckDuration()
block_duration = portal_preferences.getPreferredAuthenticationFailureBlockDuration()
max_authentication_failures = portal_preferences.getPreferredMaxAuthenticationFailure()

if None in (check_duration,
            block_duration,
            max_authentication_failures):
  log('Login block is not working because authentication policy in system preference is not set properly.')
  return 0

check_time = now - check_duration*one_second

# some failures might be still unindexed
tag = 'authentication_event_%s' %context.getReference()
unindexed_failures = portal.portal_activities.countMessageWithTag(tag)

if unindexed_failures >= max_authentication_failures:
  # no need to check further
  return 1

# some are already indexed
kw = {'portal_type': 'Authentication Event',
      'default_destination_uid': context.getUid(),
      'creation_date': Query(creation_date = check_time,
                             range='min'),
      'validation_state' : 'confirmed',
      'sort_on' : (('creation_date', 'ASC',),),
      'limit': max_authentication_failures
      }
indexed_failure_list = portal.portal_catalog(**kw)
indexed_failures = len(indexed_failure_list)

#context.log('== %s %s %s' %(unindexed_failures, indexed_failures, max_authentication_failures))
if (indexed_failures + unindexed_failures) >= max_authentication_failures:
  last_authentication_failure = indexed_failure_list[-1].getObject()
  block_timeout = last_authentication_failure.getCreationDate() + block_duration*one_second
  if block_timeout >= now:
    #context.log('block %s' %context.getReference())
    request.set('is_user_account_blocked', True)
    return 1

return 0
