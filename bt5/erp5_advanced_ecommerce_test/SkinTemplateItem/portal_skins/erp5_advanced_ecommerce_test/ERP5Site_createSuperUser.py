acl_users = context.getPortalObject().acl_users
if not acl_users.getUserById('super_user'):
  acl_users.zodb_users.manage_addUser(
      user_id='super_user',
      login_name='super_user',
      password='super_user',
      confirm='super_user',
  )
  acl_users.zodb_roles.manage_assignRoleToPrincipals('Manager', ('super_user',))
return 'Done'
