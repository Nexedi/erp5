"""
  Returns if password is valid or not. 
  If not valid return a negative code to indicate failure.
"""
from Products.Formulator.Errors import ValidationError
from DateTime import DateTime
import re

MARKER = ['', None]

portal = context.getPortalObject()
request = context.REQUEST
is_temp_object = context.isTempObject()
result_code_list = []
min_password_length = portal.portal_preferences.getPreferredMinPasswordLength()

if password is None:
  # means simply that password will be reseted in this case 
  # it's a valid value (i.e. it's job of form validation yo handle this in UI appropriately)
  return []

# not long enough
if min_password_length is not None:
  if len(password) < min_password_length:
    result_code_list.append(-1)

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
    result_code_list.append(-2)

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
    result_code_list.append(-3)

  # not already used before ?
  preferred_number_of_last_password_to_check = portal.portal_preferences.getPreferredNumberOfLastPasswordToCheck()
  if preferred_number_of_last_password_to_check not in [None, 0]:
    if context.isPasswordAlreadyUsed(password):
      result_code_list.append(-4)

# not contain the full name of the user in password or any parts of it (i.e. last and / or first name)
if portal.portal_preferences.isPrefferedForceUsernameCheckInPassword():
  lower_password = password.lower()
  if not is_temp_object:
    # real object
    first_name = context.getFirstName()
    last_name = context.getLastName()
  else:
    # temporary object
    first_name = getattr(context, 'first_name', None)
    last_name = getattr(context, 'last_name', None)

  if first_name not in MARKER:
    first_name = first_name.lower()
  if last_name not in MARKER:
    last_name = last_name.lower()

  if (first_name not in MARKER and first_name in lower_password) or \
    (last_name not in MARKER  and last_name in lower_password):
    # user's name must not be contained in password
    result_code_list.append(-5)

return result_code_list
