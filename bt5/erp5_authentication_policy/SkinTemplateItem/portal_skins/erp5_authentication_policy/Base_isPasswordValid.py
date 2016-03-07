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

def doValidation(person, password):
  # raise so Formulator shows proper message
  result_code_list = person.Person_analyzePassword(password)
  if result_code_list!=[]:
    translateString = context.Base_translateString
    message = ' '.join([translateString(message_dict[x]) for x in result_code_list])
    raise ValidationError('external_validator_failed', context, error_text=message)
  return 1

user_login = request.get('field_user_login', None)
# find Person object (or authenticated member) and validate it on it (password recovered for an existing account)
person = context.ERP5Site_getAuthenticatedMemberPersonValue(user_login)
if person is not None:
  return doValidation(person, password)

# use a temp object (new account created)
first_name = request.get('field_your_first_name', None) 
last_name = request.get('field_your_last_name', None) 
kw = {'title': '%s %s' %(first_name, last_name),
      'first_name': first_name,
      'last_name': last_name}
person = newTempBase(portal, kw['title'], **kw)

return doValidation(person, password)
