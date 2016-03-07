"""External Validator for Person_viewDetails/my_password
checks that password and confimation matches.
"""
password_confirm = request.get('field_password_confirm',
                               request.get('password_confirm'))

if password_confirm == editor :
  return 1
return 0
