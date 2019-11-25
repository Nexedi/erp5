"""
This script returns a list of dictionaries which represent
the security groups which a person is member of. It extracts
the categories from the current content and associates
it to a given base_category. It is useful in the
following cases:

- calculate a security group based current object 
  in the context of a base category (ex. source_project).
  This is used for example in ERP5 DMS to calculate
  project security.

The parameters are

  base_category_list -- list of category values we need to retrieve
  user_name          -- string obtained from getSecurityManager().getUser().getId()
  ob                 -- object which we want to assign roles to
  portal_type        -- portal type of object

NOTE: for now, this script requires proxy manager
"""

category_list = []

if ob is None:
  return []

for base_category in base_category_list:
  category_list.append({base_category: ob.getRelativeUrl()})

return category_list
