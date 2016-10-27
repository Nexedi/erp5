# get the current logged user site

from Products.ERP5Type.Cache import CachingMethod

if user_id is None:
  user_id = context.portal_membership.getAuthenticatedMember().getId()

def getGroupList(user_id=user_id):

  valid_assignment = context.Baobab_getUserAssignment(user_id=user_id)

  group_list = []
  if valid_assignment != None:
    new_group = valid_assignment.getGroup()
    if not new_group.startswith('group'):
      new_group='group/%s' % new_group
    if new_group not in ('', None):
      group_list.append(new_group)
  return group_list

getGroupList = CachingMethod(getGroupList, id='Baobab_getUserAssignedGroupList', cache_factory='erp5_ui_short')
return getGroupList(user_id=user_id)
