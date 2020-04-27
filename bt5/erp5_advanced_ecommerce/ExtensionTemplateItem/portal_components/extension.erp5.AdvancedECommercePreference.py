from AccessControl.SecurityManagement import getSecurityManager, \
             setSecurityManager, newSecurityManager
from Products.ERP5Security import SUPER_USER


def immediateReindex(self):
  self.immediateReindexObject()

def executeMethodAsSuperUser(self, method,**kw):
  sm = getSecurityManager()
  try:
    newSecurityManager(self.REQUEST, self.getPortalObject().acl_users.getUser(SUPER_USER))
    method = getattr(self, method)
    return method(**kw)
  finally:
    #Restore orinal user
    setSecurityManager(sm)
