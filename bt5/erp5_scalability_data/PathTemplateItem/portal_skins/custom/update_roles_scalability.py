portal = context.getPortalObject()
portal_types = portal.searchFolder(title='portal_types')[0]
role_name_list = ['Assignor', 'Assignee', 'Associate', 'Auditor', 'Author']
role_category_list = ['group/my_group']

role_list = ['Product', 'Product Module', 'Person', 'Person Module', 
                  'Organisation', 'Organisation Module', 'Sale Trade Condition',
                  'Sale Trade Condition Module', 'Web Page Module', 'Sale Order Module']


for role in role_list:

  # Get portal type
  current_portal = portal_types.searchFolder(title={'query':role, 'key':'ExactMatch'})[0]

  # Delete existing role informations
  id_list =  [x.getId() for x in current_portal.searchFolder(portal_type='Role Information')]
  current_portal.manage_delObjects(id_list)

  # Create new role information
  current_portal.newContent(
                    portal_type = 'Role Information',
                    title = 'Default',
                    role_name_list = role_name_list,
                    role_category_list = role_category_list,
                    description = 'Configured by Scalability script'
                   )
  # Update roles
  current_portal.updateRoleMapping()

return 1
