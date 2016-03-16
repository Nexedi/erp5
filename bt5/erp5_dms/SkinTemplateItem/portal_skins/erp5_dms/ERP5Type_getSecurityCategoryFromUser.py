"""
Get security categories from current user
XXX I'm not sure it is used anywhere at the moment.
"""

category_list = []

person_module = context.portal_url.getPortalObject().getDefaultModule('Person')
# It is better to keep getObject(), in this script this
# prevent a very strange bug, sometimes without getObject the
# assignment is not found
person_object_list = [x.getObject() for x in person_module.searchFolder(portal_type='Person', reference=user_name)]

if len(person_object_list) != 1:
  if len(person_object_list) > 1:
    raise ConsistencyError, "Error: There is more than one Person with reference '%s'" % user_name
  else:
    # if a person_object was not found in the module, we do nothing more
    # this happens for example when a manager with no associated person object
    # creates a person_object for a new user
    return []
person_object = person_object_list[0]

category_dict = {}
for base_category in base_category_list:
  category_value = person_object.getProperty(base_category)
  if category_value not in (None, ''):
    category_dict[base_category] = category_value
  else:
    raise RuntimeError, "Error: '%s' property is required in order to update person security group"  % (base_category)
  category_list.append(category_dict)

return category_list
