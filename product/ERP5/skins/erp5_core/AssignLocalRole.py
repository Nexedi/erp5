# Assign to each user in the user_list all
# roles inside role_list. By the same time,
# we ensure that nobody else have one of
# the role of role_list

for role in role_list:
  for user in context.users_with_local_role(role):
    temp_roles = []
    user_roles = context.get_local_roles_for_userid(user)
    for i in range(0,len(user_roles)):
      if user_roles[i]!=role:
        temp_roles+=[user_roles[i]]
        #user_roles = user_roles[0:i] + user_roles[i+1:len(user_roles)]
    if len(temp_roles) is not 0:
      context.manage_setLocalRoles(user,temp_roles)
    else:
      context.manage_delLocalRoles((user,))
# Add roles to users
for user in user_list:
  context.manage_addLocalRoles(user, role_list)
