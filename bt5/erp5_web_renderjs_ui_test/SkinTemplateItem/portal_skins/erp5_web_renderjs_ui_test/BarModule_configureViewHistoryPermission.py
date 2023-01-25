default_permission_list = [permission['name'] for permission in context.bar_module.permissionsOfRole('Manager') if permission['selected'] == 'SELECTED']

if value:
  if 'View History' not in default_permission_list:
    default_permission_list.append('View History')
else:
  if 'View History' in default_permission_list:
    default_permission_list.remove('View History')

context.bar_module.manage_role('Manager', default_permission_list)

return 'Done'
