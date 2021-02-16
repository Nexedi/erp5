# Get the user id of the context owner.
local_role_list = context.get_local_roles()
for group, role_list in local_role_list:
  if 'Owner' in role_list:
    return group
raise ValueError('Context (%r) has no owner (see local roles).' % context)
