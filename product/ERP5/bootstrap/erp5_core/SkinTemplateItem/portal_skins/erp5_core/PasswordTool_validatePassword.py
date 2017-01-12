"""External validator for PasswordTool_viewResetPassword/your_password

Check that the provided password matchs with the confirmation
and if authentication policy is enabled, that the password match the policy.
"""
from Products.Formulator.Errors import ValidationError
password_confirm = request.get('field_password_confirm',
                               request.get('password_confirm'))

# password does not match confirmation, returns the default external validator message.
if password_confirm != editor:
  return 0

password_key = request.get('field_your_password_key',
                           request.get('your_password_key'))
assert password_key

validation_message_list = context.analyzePassword(editor, password_key)
if validation_message_list:
  message = u' '.join([str(x) for x in validation_message_list])
  raise ValidationError('external_validator_failed', context, error_text=message)

return 1
