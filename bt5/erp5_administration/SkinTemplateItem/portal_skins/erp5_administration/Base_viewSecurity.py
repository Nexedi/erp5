from AccessControl import getSecurityManager
from pprint import pformat

u = getSecurityManager().getUser()

user_value = u.getUserValue()
if user_value is None:
  print('User ID:', u.getId())
else:
  print('User ID:', u.getId(), user_value.getPath())
login_value = u.getLoginValue()
if login_value is None:
  print('Login:', u.getUserName())
else:
  print('Login:', u.getUserName(), login_value.getPath())
print('Is owner:', u.allowed(context,('Owner',)))
print('User roles:', u.getRoles())
print('User roles in context:', u.getRolesInContext(context))
print('Permissions:')
for permission in [
  'Access contents information',
  'Add portal content',
  'Delete objects',
  'Modify portal content',
  'View',
  'Manage portal',
]:
  print(" ", permission, u.has_permission(permission, context))

print()
try:
  print("User groups:\n", pformat(sorted(u.getGroups())))
except AttributeError:
  print('no getGroups')

print()
print('Local roles on document:\n', pformat(context.get_local_roles()))

return printed
