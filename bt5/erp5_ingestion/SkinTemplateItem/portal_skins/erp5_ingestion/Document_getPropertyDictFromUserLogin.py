"""
Gets document properties discovered from the user who contributes / owns the document.
User would be usually the current user, but sometimes the name has to be given explicitly
if e.g. the doc is contributed by email, and the script is run by zope user.
"""
import six
assignment_dict = context.ERP5Site_getPersonAssignmentDict(user_name=user_name)
group_list = assignment_dict['group_list']

if group_list:
  group_level_dict = {}
  for group in group_list:
    group_level = len(group.split("/"))
    group_level_dict[group] = group_level

  #Get the highest levels groups of the assignments
  ##if group_list = ['g1', 'g1/g1.1', 'g1/g1.2'] returns ['g1']
  ##if group_list = ['g1/g1.1', 'g1/g1.2'] returns ['g1/g1.1', 'g1/g1.2']
  highest_level_group_value = min(six.itervalues(group_level_dict))
  highest_level_group_list = [k for k in group_level_dict if group_level_dict[k] == highest_level_group_value]
  return {'group_list': highest_level_group_list}

return {}
