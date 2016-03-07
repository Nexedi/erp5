"""External Validator for Person_viewDetails/my_password
checks that password and confimation matches.
"""
# XXX: unify
password_confirm = request.get('field_your_password',
                               request.get('your_password'))

if password_confirm == editor :
  return 1
return 0
