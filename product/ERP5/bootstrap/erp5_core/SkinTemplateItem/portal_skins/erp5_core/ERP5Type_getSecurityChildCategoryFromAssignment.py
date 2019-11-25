"""
This script returns a list of dictionaries which represent
the security groups which a person is member of. It extracts
the categories from the current user assignment.
It is useful in the following cases:

- associate a document (ex. an accounting transaction)
  to the division which the user was assigned to
  at the time it was created

- calculate security membership of a user

The parameters are

  base_category_list -- list of category values we need to retrieve
  user_name          -- string obtained from getSecurityManager().getUser().getId()
  ob                 -- object which we want to assign roles to
  portal_type        -- portal type of object

NOTE: for now, this script requires proxy manager
"""

category_list = []

person_object = context.Base_getUserValueByUserId(user_name)
if person_object is None:
  # if a person_object was not found in the module, we do nothing more
  # this happens for example when a manager with no associated person object
  # creates a person_object for a new user
  return []
# We look for every valid assignments of this user
for assignment in person_object.contentValues(filter={'portal_type': 'Assignment'}):
  if assignment.getValidationState() == 'open':
    category_dict = {}
    for base_category in base_category_list:
      category_value_list = assignment.getAcquiredValueList(base_category)
      if category_value_list:
        for category_value in category_value_list:
          category_dict.setdefault(base_category, []).append('%s*' % category_value.getRelativeUrl())
    category_list.append(category_dict)

return category_list
