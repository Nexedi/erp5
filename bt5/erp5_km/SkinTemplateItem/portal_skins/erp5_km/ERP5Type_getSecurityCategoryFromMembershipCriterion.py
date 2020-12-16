"""
This script returns a list of dictionaries which represent
the security groups to define a local role. It extracts
the categories from the current membership criterion
of a Predicate. It is useful in the following cases:

- assign a security group to a Web Section
  based on the member ship criterion.

The parameters are

  base_category_list -- list of acceptable base categories
                        (used to filter part of the criteria)
  user_name          -- the user identifier (not used)
  obj                -- object which we want to assign roles to
  portal_type        -- portal type of object
"""

category_list = []

if obj is None:
  return []

criterion_list = obj.getMembershipCriterionCategoryList()
for criterion in criterion_list:
  id_list = criterion.split('/')
  base_category = id_list[0]
  if base_category in base_category_list:
    category = '/'.join(id_list[1:])
    category_list.append({base_category : category})

return category_list
