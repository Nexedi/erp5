"""
WARNING: this script requires proxy manager

This script tries to acquire category values from other objects

base_category_list - list of category values we need to retrieve
object             - object which we want to assign roles to.
"""
category_dict = {}

if object is None:
  return []

for base_category in base_category_list:
  for o in object.getValueList(base_category):
    for user, role_list in o.get_local_roles():
      for role in role_list:
        if role == 'Associate':
          category_dict.setdefault('Assignee', []).append(user)
          category_dict.setdefault('Assignor', []).append(user)
          category_dict.setdefault('Auditor', []).append(user)
          category_dict.setdefault('Associate', []).append(user)

# By returning a dict, we force force ERP5Type
# to interprete the result as a mapping from
# roles to existing security groups
return category_dict
