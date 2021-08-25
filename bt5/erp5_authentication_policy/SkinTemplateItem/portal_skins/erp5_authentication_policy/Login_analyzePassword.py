"""
Returns the list of messages in case a password does not comply with the policy
"""
from Products.ERP5Type.Message import translateString
from DateTime import DateTime
import re


result_code_list = []
def addError(error_message):
  result_code_list.append(translateString(error_message))

portal = context.getPortalObject()
is_temp_object = context.isTempObject()
min_password_length = portal.portal_preferences.getPreferredMinPasswordLength()

if password is None:
  # means simply that password will be reseted in this case
  # it's a valid value (i.e. it's job of form validation to handle this in UI appropriately)
  return []

# not long enough
if min_password_length is not None:
  if len(password) < min_password_length:
    addError('Too short.')

# password contain X out of following Y regular expression groups ?
regular_expression_list = portal.portal_preferences.getPreferredRegularExpressionGroupList()
min_regular_expression_group_number = portal.portal_preferences.getPreferredMinRegularExpressionGroupNumber()
if regular_expression_list:
  group_counter = 0
  for re_expr in regular_expression_list:
    mo = re.search(re_expr, password)
    if mo is not None and len(mo.groups()):
      group_counter+=1
  #context.log('%s %s %s %s' %(password, group_counter, min_regular_expression_group_number, regular_expression_list))
  if group_counter < min_regular_expression_group_number:
    # not enough groups match
    addError('Not complex enough.')

if not is_temp_object:
  # not changed in last period ?
  now = DateTime()
  one_hour = 1/24.0
  min_password_lifetime_duration = portal.portal_preferences.getPreferredMinPasswordLifetimeDuration()
  #last_password_modification_date = context.getLastPasswordModificationDate()
  last_password_modification_date = None
  last_password_event = portal.portal_catalog.getResultValue(
                                                portal_type = 'Password Event',
                                                default_destination_uid = context.getUid(),
                                                validation_state = 'confirmed',
                                                sort_on = (('creation_date', 'DESC',),))
  if last_password_event is not None:
    last_password_modification_date = last_password_event.getCreationDate()

  if last_password_modification_date is not None and \
    min_password_lifetime_duration is not None and \
    (last_password_modification_date + min_password_lifetime_duration*one_hour) > now:
    # too early to change password
    addError('You have changed your password too recently.')

  # not already used before ?
  if portal.portal_preferences.getPreferredNumberOfLastPasswordToCheck():
    if context.isPasswordAlreadyUsed(password):
      addError('You have already used this password.')

# not contain the full name of the user in password or any parts of it (i.e. last and / or first name)
if portal.portal_preferences.isPrefferedForceUsernameCheckInPassword():
  lower_password = password.lower()
  if not is_temp_object:
    # real object
    first_name = getattr(context, 'getFirstName', context.getTitle)()
    last_name = getattr(context, 'getLastName', context.getReference)()
  else:
    # temporary object
    first_name = getattr(context, 'first_name', None)
    last_name = getattr(context, 'last_name', None)

  if first_name:
    first_name = first_name.lower()
  if last_name:
    last_name = last_name.lower()

  if (first_name and first_name in lower_password) or \
    (last_name and last_name in lower_password):
    # user's name must not be contained in password
    addError('You can not use any parts of your first and last name in password.')

return result_code_list
