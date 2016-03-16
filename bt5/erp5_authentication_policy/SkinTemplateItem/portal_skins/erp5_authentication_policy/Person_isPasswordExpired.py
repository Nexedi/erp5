"""
  Returns if user account is Person's password is expired.
  Start password recovery process for expired password (if configured).
"""
from Products.ERP5Type.Cache import CachingMethod

request = context.REQUEST
portal = context.getPortalObject()

def _isPasswordExpired():
  from DateTime import DateTime
  one_hour = 1/24.0
  now = DateTime()
  max_password_lifetime_duration = portal.portal_preferences.getPreferredMaxPasswordLifetimeDuration()
  password_lifetime_expire_warning_duration = portal.portal_preferences.getPreferredPasswordLifetimeExpireWarningDuration()
  last_password_event = portal.portal_catalog.getResultValue(
                                                portal_type = 'Password Event',
                                                default_destination_uid = context.getUid(),
                                                validation_state = 'confirmed',
                                                sort_on = (('creation_date', 'DESC',),))
  expire_date_warning = 0 
  if last_password_event is not None:
    last_password_modification_date = last_password_event.getCreationDate()
    expire_date = last_password_modification_date + max_password_lifetime_duration*one_hour 
    if password_lifetime_expire_warning_duration not in (0, None,):
      # calculate early warning period
      if now > expire_date - password_lifetime_expire_warning_duration*one_hour and \
         expire_date > now:
        expire_date_warning =  expire_date
    if expire_date < now:
      # password is expired
      #context.log('expired %s' %context.getReference())
      return True, expire_date_warning
  return False, expire_date_warning

_isPasswordExpired = CachingMethod(_isPasswordExpired,
                                   id='Person_isPasswordExpired_%s' %context.getReference(),
                                   cache_factory='erp5_content_short')
is_password_expired, expire_date = _isPasswordExpired()

request.set('is_user_account_password_expired', is_password_expired)
request.set('is_user_account_password_expired_expire_date', expire_date)

return is_password_expired
