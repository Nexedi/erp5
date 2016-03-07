"""
  External Validator for WebSite_createWebSiteAccountForm/your_password
  that checks that password and password confimation matches.
"""
password_confirm = request.get('field_your_password_confirm', request.get('password_confirm'))
if password_confirm == editor:
  return 1
return 0
