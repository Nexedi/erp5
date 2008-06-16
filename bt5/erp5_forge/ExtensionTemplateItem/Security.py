def viewSecurityAsUser(self, login):
  from AccessControl import getSecurityManager
  from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
  user_folder = self.getPortalObject().acl_users
  sm = getSecurityManager()
  try:
    new_user = user_folder.getUserById(login)
    newSecurityManager(user_folder, new_user)
    st = self.Base_viewSecurity()
  finally:
    setSecurityManager(sm)
  return st