from Products.PluggableAuthService.UserPropertySheet import UserPropertySheet
if isinstance(UserPropertySheet, type): # new-stype class
  # to unpickle instances that are picked as old-style class.
  # this happens when a OAuth2 logged in user creates an activity on Zope2
  # then the system is upgraded to Zope4.
  __init__orig = UserPropertySheet.__init__
  def __init__new(self, id=None, schema=None, **kw):
    __init__orig(self, id, schema, **kw)
  UserPropertySheet.__init__ = __init__new
