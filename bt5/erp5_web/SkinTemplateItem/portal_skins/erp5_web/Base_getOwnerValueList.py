"""
  Returns the list of owners of the given context. Owners
  are normally Person objects in ERP5. However, this behaviour
  could be extended in the future or for specific projects.

  NOTE: we usually asume that there is only a single owner
  or that, at least,  only the first owner matters for
  the "My Documents" list.

  TODO:
  - how can we make sure that is is consistent with 
    ERP5Site_getAuthenticatedMemberPersonValue 
    in erp5_base ?
"""
from zExceptions import Unauthorized
owner_value_list = []
try:
  owner_id_list = [i[0] for i in context.get_local_roles() if 'Owner' in i[1]]
except Unauthorized:
  owner_id_list = []

if len(owner_id_list):
  return context.portal_catalog(portal_type='Person', reference=owner_id_list)
else:
  return []
