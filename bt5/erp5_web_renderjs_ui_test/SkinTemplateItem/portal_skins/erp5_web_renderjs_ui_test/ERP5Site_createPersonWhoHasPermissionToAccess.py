acl_users = context.getPortalObject().acl_users
if not acl_users.getUserById('user_logout_test'):
  acl_users.zodb_users.manage_addUser(
      user_id='user_logout_test',
      login_name='user_logout_test',
      password='user_logout_test',
      confirm='user_logout_test',
  )
  # BBB for PAS 1.9.0 we pass a response and undo the redirect
  response = container.REQUEST.RESPONSE
  acl_users.zodb_roles.manage_assignRoleToPrincipals(
      'Manager',
      ('user_logout_test',),
      RESPONSE=response)
  response.setStatus(200)
return 'done'
