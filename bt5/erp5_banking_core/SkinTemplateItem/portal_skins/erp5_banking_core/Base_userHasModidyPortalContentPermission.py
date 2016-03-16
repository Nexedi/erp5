"""
This script is used to determine if the user
has the permission "Modify portal content",
in the context
"""
from AccessControl import getSecurityManager
u=getSecurityManager().getUser()
if u.has_permission("Modify portal content",context):
  return True
else:
  return False
