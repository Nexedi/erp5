acl_users = context.getPortalObject().acl_users
if not acl_users.getUserById('super_user'):
  acl_users.zodb_users.manage_addUser(
      user_id='super_user',
      login_name='super_user',
      password='super_user',
      confirm='super_user',
  )
  # BBB for PAS 1.9.0 we pass a response and undo the redirect
  response = container.REQUEST.RESPONSE
  acl_users.zodb_roles.manage_assignRoleToPrincipals(
      'Manager',
      ('super_user',),
      RESPONSE=response)
  response.setStatus(200)

return 'Done'
