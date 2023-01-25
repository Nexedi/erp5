"""
WARNING: this script requires proxy manager

This script tries to acquire category values from other documents

base_category_list - list of category values we need to retrieve
obj                - document which we want to assign roles to.
"""
category_dict = {}

if obj is None:
  return []

for base_category in base_category_list:
  if base_category == 'parent':
    o_list = [obj.getParentValue()]
  else:
    o_list = obj.getValueList(base_category)
  for o in o_list:
    for user, role_list in o.get_local_roles():
      for role in role_list:
        category_dict.setdefault(role, []).append(user)

# By returning a dict, we force force ERP5Type
# to interprete the result as a mapping from
# roles to existing security groups
return category_dict
