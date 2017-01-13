# Proxy roles: Manager to access PAS API.
for user in context.acl_users.searchUsers(
  login=reference,
  exact_match=True,
  login_portal_type=portal_type,
):
  login_list = user.get('login_list')
  if login_list is None:
    # Forbid non-ERP5 logins from being reused in-ERP5.
    return True
  if user['uid'] == ignore_user_uid:
    continue
  for login in login_list:
    if login['uid'] != ignore_uid:
      return True
return False
