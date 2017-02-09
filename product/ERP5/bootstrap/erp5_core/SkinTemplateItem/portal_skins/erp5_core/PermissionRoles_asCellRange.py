managed_permissions = sorted(context.getParent().getWorkflowManagedPermissionList())
available_roles = context.getManagedRoleList()

ma_i = []
ma_j = []

if matrixbox:
  for perms in managed_permissions:
    ma_i.append([perms,perms])
  for roles in available_roles:
    ma_j.append([roles, roles])
  return [ma_i, ma_j]
