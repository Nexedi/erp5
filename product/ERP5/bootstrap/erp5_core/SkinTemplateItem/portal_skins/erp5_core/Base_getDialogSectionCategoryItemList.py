"""Return the section_category the user can select in reports.

By default, if the current user is a person, only the groups for which the user
has open assignment can be selected.
"""

portal = context.getPortalObject()

group_title_item_list = portal.Base_getPreferredCategoryChildItemList(
    portal.portal_categories.group,
    base=True,
)

zope_user = portal.portal_membership.getAuthenticatedMember()
if 'Manager' in zope_user.getRolesInContext(context):
  return group_title_item_list

user = zope_user.getUserValue()
if getattr(user, 'getPortalType', lambda: None)() != 'Person':
  return group_title_item_list

allowed_group_set = {
    a.getGroup(base=True)
    for a in user.Person_getAvailableAssignmentValueList()
}
allowed_group_set = {g for g in allowed_group_set if g}

filtered_group_title_item_list = [['', '']]
for group_title, group_relative_url in group_title_item_list:
  if group_relative_url and any(
      allowed_group for allowed_group in allowed_group_set
      if group_relative_url.startswith(allowed_group + '/')
      or group_relative_url == allowed_group):
    filtered_group_title_item_list.append([group_title, group_relative_url])
return filtered_group_title_item_list
