"""
  Expire old Authentication Events.
"""
from DateTime import DateTime
from Products.ZSQLCatalog.SQLCatalog import Query

portal = context.getPortalObject()
portal_preferences = portal.portal_preferences

now = DateTime()
one_second = 1/24.0/60.0/60.0
check_duration = portal_preferences.getPreferredAuthenticationFailureCheckDuration()
check_time = now - check_duration*one_second

kw = {'portal_type': 'Authentication Event',
      'creation_date': Query(creation_date = check_time,
                             range='max'),
      'validation_state' : 'confirmed'}
failure_list = portal.portal_catalog(**kw)

for failure in failure_list:
  tag = 'expire_%s' %failure.getUid()
  failure.activate(tag = tag).expire(comment='System expire.')
  failure.activate(after_tag = tag).reindexObject()
