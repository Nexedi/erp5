# Proxy roles: Manager to access searchUsers
if REQUEST is not None:
  return
user_id_set = {x['id'] for x in context.acl_users.searchUsers(
  login=user_name,
  exact_match=True,
)}
if len(user_id_set) == 1:
  user_id, = user_id_set
  return user_id
