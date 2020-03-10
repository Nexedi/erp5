"""
This is for calculating permissions to a Person object
we take categories from his Assignments, so we don't look for
Person, just take from the object.
"""

# XXX could use some refactoring...

category_list = []

# We look for valid assignments of this user
for assignment in obj.contentValues(filter={'portal_type': 'Assignment'}):
  if assignment.getValidationState() == 'open':
    category_dict = {}
    for base_category in base_category_list:
      if base_category == 'follow_up':
        category_value = assignment.getDestinationProject()
      else:
        category_value = assignment.getProperty(base_category)
      if category_value not in (None, ''):
        category_dict[base_category] = category_value
      else:
        raise RuntimeError("Error: '%s' property is required in order to update person security group"  % (base_category))
    category_list.append(category_dict)

return category_list
