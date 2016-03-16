""" Retrieve the role list of the Node. """
role_list = []

for role in context.getRoleList():
  role_list.append("role/%s" %(role))

role_list.sort()

return role_list
