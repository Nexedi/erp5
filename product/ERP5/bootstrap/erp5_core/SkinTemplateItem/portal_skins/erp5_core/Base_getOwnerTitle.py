"""Returns the name of the owner of current document
"""
owner_id_list = [i[0] for i in context.get_local_roles() if 'Owner' in i[1]]
if owner_id_list:
  found_user_list = [x for x in context.acl_users.searchUsers(id=tuple(owner_id_list), exact_match=True) if 'path' in x]
  if found_user_list:
    found_user, = found_user_list
    return context.getPortalObject().restrictedTraverse(found_user['path']).getTitle()
  return owner_id_list[0]
