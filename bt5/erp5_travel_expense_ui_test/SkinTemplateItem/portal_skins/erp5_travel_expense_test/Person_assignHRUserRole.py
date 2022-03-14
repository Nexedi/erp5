if context.person_module.hr_user.contentValues(portal_type='ERP5 Login'):
  return 'ok'

acl_users = context.getPortalObject().acl_users
user_id = context.person_module.hr_user.getUserId()
response = container.REQUEST.RESPONSE
acl_users.zodb_roles.manage_assignRoleToPrincipals('Manager',(user_id,),RESPONSE=response)

assignment = context.person_module.hr_user.newContent(
  portal_type="Assignment")
assignment.open()
login = context.person_module.hr_user.newContent(portal_type='ERP5 Login', reference='test', password='test')
login.validate()



response.setStatus(200)

return 'ok'
