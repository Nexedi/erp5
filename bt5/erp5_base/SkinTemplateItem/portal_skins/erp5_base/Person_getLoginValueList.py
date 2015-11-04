def migrateLogin():
  login = context.newContent(
    portal_type='Login',
    reference=context.getReference(),
    password=context.getPassword(),
  )
  login.validate()
  return login

login_list = context.objectValues(portal_type='Login')

if not login_list:
  return [migrateLogin()]
elif not [x for x in login_list if x.getValidationState() == 'validated']:
  return [migrateLogin()] + login_list
else:
  return login_list
