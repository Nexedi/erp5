# XXX This script might also need proxy Manager
# XXX This script could be deleted after the full transition to PAS (don't forget to update assignment workflow too)

# user_folder: NuxUserGroups or PluggableAuthService at the root of the ERP5Site.
user_folder = context.portal_url.getPortalObject()['acl_users']

# This script can be bypassed in the context of PAS use because user groups are
#   automaticcaly managed and set by ERP5Security/ERP5GroupManage.py
if user_folder.meta_type == 'Pluggable Auth Service':
  return

# base_category_list : list of category values we want to retrieve
# XXX Keep the same order as in the Portal Types Roles Definitions.
#  -> No longer true since this list is always sorted by the ERP5Type_asSecurityGroupId script.
base_category_list = context.getPortalObject().getPortalAssignmentBaseCategoryList()

# user_name : string representing the user whom we want to modify the groups membership
user_name = context.getId()

# Verify the existence of the user
# XXX Note : sometimes, you don't want to update security for users who don't belong to your organisation.
#            You can then add code in the assignment_workflow script to skip those (if role != internal for instance)
if user_name not in user_folder.getUserNames():
  raise RuntimeError("Error: Zope user %r doesn't exist in the acl_users folder"  % user_name)

category_list = []
security_group_list = []

# Fetch category values from assignment
category_list.extend(context.ERP5Type_getSecurityCategoryFromAssignment(base_category_list, user_name, context, ''))

# Get group names from category values
for c_dict in category_list:
  security_group_list.append(context.ERP5Type_asSecurityGroupId(category_order=base_category_list, **c_dict))

# Get the id list of existing groups
existing_group_list = user_folder.getGroupNames()

# Create groups if they don't exist
for group in security_group_list:
  if group not in existing_group_list:
    user_folder.userFolderAddGroup(group)

# Proceed with group assignment
user_folder.setGroupsOfUser(security_group_list, user_name)
