"""
  Returns if user account is Person's password is expired.
  Start password recovery process for expired password (if configured).
"""
portal = context.getPortalObject()
is_password_expired = False
expire_date_warning = 0
password_event_list = portal.portal_catalog(
  select_list=['creation_date'],
  portal_type='Password Event',
  default_destination_uid=context.getUid(),
  validation_state='confirmed',
  sort_on=(('creation_date', 'DESC'), ),
  limit=1,
)
if password_event_list:
  ONE_HOUR = 1 / 24.0
  portal_preferences = portal.portal_preferences
  max_password_life_time = portal_preferences.getPreferredMaxPasswordLifetimeDuration()
  # If auto created by system, user have to change maximum after one day
  if password_event_list[0].getTitle().startswith('auto creation'):
    expire_date = password_event_list[0].creation_date + (24 if 24 < max_password_life_time else max_password_life_time) * ONE_HOUR
  else:
    expire_date = password_event_list[0].creation_date + max_password_life_time * ONE_HOUR
  now = DateTime()
  if expire_date < now:
    # password is expired
    is_password_expired = True
  else:
    password_lifetime_expire_warning_duration = portal_preferences.getPreferredPasswordLifetimeExpireWarningDuration()
    if password_lifetime_expire_warning_duration and now > expire_date - password_lifetime_expire_warning_duration * ONE_HOUR:
      expire_date_warning = expire_date
else:
  # No password event means user doesn't yet change password
  # Auto Create a password event
  # so we can use passwordExpired functionnality to force user to change it
  password_event = portal.system_event_module.newContent(portal_type='Password Event',
                                                         title='auto creation for %s' % context.getReference(),
                                                         source_value=context,
                                                         destination_value=context,
                                                         password=context.getPassword())
  password_event.confirm(comment='auto creation')

request = portal.REQUEST
request.set('is_user_account_password_expired', is_password_expired)
request.set('is_user_account_password_expired_expire_date', expire_date_warning)
return is_password_expired
