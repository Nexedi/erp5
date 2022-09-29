"""
WARNING: this script requires proxy manager

This script tries to acquire category values from other object
through reverse relation (ex. getAggregateRelatedValueList)

base_category_list - list of category values we need to retrieve
object             - object which we want to assign roles to.

TODO: how do be sure that the related object is already
indexed ? XXX
"""
category_dict = {}

if object is None:
  return []

for base_category in base_category_list:
  for o in object.getRelatedValueList(base_category):
    for user, role_list in o.get_local_roles():
      for role in role_list:
        if role in ('Assignor', 'Assignee'):
          category_dict.setdefault(role, []).append(user)

# By returning a dict, we force force ERP5Type
# to interprete the result as a mapping from
# roles to existing security groups
return category_dict
