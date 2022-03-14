"""
Get security categories from current user
XXX I'm not sure it is used anywhere at the moment.
"""

category_list = []

person_object = context.Base_getUserValueByUserId(user_name)
if person_object is None:
  # if a person_object was not found in the module, we do nothing more
  # this happens for example when a manager with no associated person object
  # creates a person_object for a new user
  return []

category_dict = {}
for base_category in base_category_list:
  category_value = person_object.getProperty(base_category)
  if category_value not in (None, ''):
    category_dict[base_category] = category_value
  else:
    raise RuntimeError("Error: '%s' property is required in order to update person security group"  % base_category)
  category_list.append(category_dict)

return category_list
