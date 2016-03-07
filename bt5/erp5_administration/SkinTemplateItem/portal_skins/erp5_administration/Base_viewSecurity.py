from AccessControl import getSecurityManager
from zExceptions import Unauthorized
from pprint import pformat

u = getSecurityManager().getUser()

print 'User:', u
print 'Is owner:', u.allowed(context,('Owner',))
print 'User roles:', u.getRoles()
print 'User roles in context:', u.getRolesInContext(context)
print 'Permissions:'
for permission in [
  'Access contents information',
  'Add portal content',
  'Delete objects',
  'Modify portal content',
  'View',
  'Manage portal',
]:
  print " ", permission, u.has_permission(permission, context)

print
try:
  print "User groups:\n", pformat(u.getGroups())
except AttributeError:
  print 'no getGroups'

print
print 'Local roles on document:\n', pformat(context.get_local_roles())

print '''
----------------
Security mapping
----------------'''
if u.getId() is not None:
  try:
    print context.Base_viewSecurityMappingAsUser(u.getId())
  except Unauthorized:
    print "user doesn't have permission to security mapping in this context"

return printed
