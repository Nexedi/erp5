allow = False
def match(criterion_list, reference_list):
  for criterion in criterion_list:
    if criterion in reference_list:
      return True
  return False

if not allow and role_list is not None:
  from AccessControl import getSecurityManager
  roles = getSecurityManager().getUser().getRoles()
  allow = match(roles, role_list)

if not allow and function_list is not None or group_list is not None:
  if function_list is None:
    function_list = []
  if group_list is not None:
    function_list.extend(context.Baobab_getFunctionList(group_list=group_list))
  user_function_list = context.Baobab_getUserAssignedFunctionList()
  allow = match(user_function_list, function_list)
return allow
