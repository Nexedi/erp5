"""
  Returns the list of owners of the given context. Owners
  are normally Person objects in ERP5. However, this behaviour
  could be extended in the future or for specific projects.

  NOTE: we usually asume that there is only a single owner
  or that, at least,  only the first owner matters for
  the "My Documents" list.
"""
from zExceptions import Unauthorized
getUserValueByUserId = context.Base_getUserValueByUserId
try:
  owner_id_list = [getUserValueByUserId(i[0]) for i in context.get_local_roles() if 'Owner' in i[1]]
except Unauthorized:
  owner_id_list = []
return [x for x in owner_id_list if x is not None]
