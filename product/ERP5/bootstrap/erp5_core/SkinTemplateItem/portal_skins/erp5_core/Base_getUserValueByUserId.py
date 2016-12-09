# Proxy roles: Manager to access searchUsers
if REQUEST is not None:
  return
user_path_set = {x['path'] for x in context.acl_users.searchUsers(
  id=user_id,
  exact_match=True,
) if 'path' in x}
if user_path_set:
  user_path, = user_path_set
  return context.getPortalObject().restrictedTraverse(user_path)
