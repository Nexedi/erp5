"""
 Creates the functional test user, validate and open assignment.
"""
portal = context.getPortalObject()
howto_dict = context.Zuite_getHowToInfo()
uf = portal.acl_users
manager_username = howto_dict['manager_username']
manager_password = howto_dict['manager_password']
uf._doAddUser(manager_username, manager_password, ['Manager'], [])

return 'Done.'
