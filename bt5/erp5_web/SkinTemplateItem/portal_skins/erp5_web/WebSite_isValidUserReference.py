"""
  Check if provided user reference is not already used in the system.
"""
user_list = context.acl_users.searchUsers(id=editor, exact_match=True)
return len(user_list)==0
