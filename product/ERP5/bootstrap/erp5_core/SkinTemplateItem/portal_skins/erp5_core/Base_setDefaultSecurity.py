permission_list = context.possible_permissions()

# First, only Manager has the permission by default
manager_permission_list = permission_list

# Then, define default ERP5 permissions
common_permission_list = [p for p in [
  'Access Transient Objects',
  'Access contents information',
  'Access session data',
  'Copy or Move',
  'List folder contents',
  'View History',
] if p in permission_list]

author_permission_list = [p for p in [
  'Add portal content',
  'Add portal folders',
] if p in permission_list]

auditor_permission_list = [p for p in [
  'View',
] if p in permission_list]

assignor_permission_list = [p for p in [
  'Modify portal content',
  'Change local roles',
  'Delete objects',
] if p in permission_list]

# Define ERP5 permissions for each role
erp5_role_dict = {
  'Assignee': common_permission_list + auditor_permission_list,
  'Assignor': common_permission_list + author_permission_list +\
              assignor_permission_list + auditor_permission_list,
  'Associate': common_permission_list + auditor_permission_list,
  'Auditor' : common_permission_list + auditor_permission_list,
  'Author': common_permission_list + author_permission_list,
  'Manager': manager_permission_list
}

# Add ERP5 permissions
erp5_permission_dict = {}
for role,permission_list in erp5_role_dict.items():
  for permission in permission_list:
    if permission not in erp5_permission_dict:
      erp5_permission_dict[permission] = []
    erp5_permission_dict[permission].append(role)

for permission,role_list in sorted(erp5_permission_dict.items()):
  # Acquire permission if the role list is same as parent
  if sorted([x['name'] for x in context.aq_parent.rolesOfPermission(permission) if x['selected']]) == sorted(role_list):
    context.manage_permission(permission, [], 1)
  else:
    context.manage_permission(permission,role_list, 0)

return "finished"
