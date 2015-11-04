"""
  Form validator which will check if password is valid for the user.
"""
from Products.ERP5Type.Document import newTempBase
from Products.Formulator.Errors import ValidationError

portal = context.getPortalObject()

message_dict = { 0: 'Unknown error',
                -1: 'Too short.',
                -2: 'Not complex enough.',
                -3: 'You have changed your password too recently.',
                -4: 'You have already used this password.',
                -5: 'You can not use any parts of your first and last name in password.'}

def doValidation(login, password):
  # raise so Formulator shows proper message
  result_code_list = login.analyzePassword(password)
  if result_code_list!=[]:
    translateString = context.Base_translateString
    message = ' '.join([translateString(message_dict[x]) for x in result_code_list])
    raise ValidationError('external_validator_failed', context, error_text=message)
  return 1

return doValidation(context, password)
