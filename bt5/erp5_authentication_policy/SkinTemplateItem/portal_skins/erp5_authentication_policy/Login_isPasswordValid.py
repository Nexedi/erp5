"""
  Form validator which will check if password is valid for the user.
"""
from Products.ERP5Type.Document import newTempBase
from Products.Formulator.Errors import ValidationError

portal = context.getPortalObject()

def doValidation(login, password):
  # raise so Formulator shows proper message
  result_message_list = login.analyzePassword(password)
  if result_message_list:
    message = u' '.join([str(x) for x in result_message_list])
    raise ValidationError('external_validator_failed', context, error_text=message)
  return 1

return doValidation(context, password)
