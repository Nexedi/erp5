"""External validator for PreferenceTool_viewChangePasswordDialog/your_password.

Check that password matchs with confirmation and that it complies to the authentication policy.
"""
from AccessControl import getSecurityManager
from Products.Formulator.Errors import ValidationError

password_confirm = request.get('field_password_confirm',
                               request.get('password_confirm'))

# password does not match confirmation, returns the default external validator message.
if password_confirm != editor:
  return 0

login = getSecurityManager().getUser().getLoginValue()
if login is not None:
  validation_message_list = login.analyzePassword(editor)
  if validation_message_list:
    message = ' '.join([str(x) for x in validation_message_list])
    raise ValidationError('external_validator_failed', context, error_text=message)

return 1
