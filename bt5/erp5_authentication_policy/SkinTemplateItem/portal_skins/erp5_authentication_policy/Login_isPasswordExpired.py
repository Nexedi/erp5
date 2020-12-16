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
  expire_date = password_event_list[0].creation_date + portal_preferences.getPreferredMaxPasswordLifetimeDuration() * ONE_HOUR
  now = DateTime()
  if expire_date < now:
    # password is expired
    is_password_expired = True
  else:
    password_lifetime_expire_warning_duration = portal_preferences.getPreferredPasswordLifetimeExpireWarningDuration()
    if password_lifetime_expire_warning_duration and now > expire_date - password_lifetime_expire_warning_duration * ONE_HOUR:
      expire_date_warning = expire_date
else:
  # No Password Event found means user doesn't yet change password
  # Force user to change it if authentication policy is configured
  if portal.portal_preferences.getPreferredMaxPasswordLifetimeDuration() is not None:
    if context.getPassword():
      is_password_expired = True

request = portal.REQUEST
request.set('is_user_account_password_expired', is_password_expired)
request.set('is_user_account_password_expired_expire_date', expire_date_warning)
return is_password_expired
