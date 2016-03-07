"""
  TODO:
  Make consistent with ERP5Site_newContent
  User cache
  XXX maybe it could/should use ERP5TypeInformation.isConstructionAllowed ???
"""

portal_object = context.getPortalObject()
try:
  module = portal_object.getDefaultModule(portal_type)
except ValueError:
  return False
if module is None:
  return False

if user is None: # can be passed directly to save resources if we are doing this many times
  from AccessControl import getSecurityManager
  user = getSecurityManager().getUser()

return user.has_permission('Add portal content', module)
