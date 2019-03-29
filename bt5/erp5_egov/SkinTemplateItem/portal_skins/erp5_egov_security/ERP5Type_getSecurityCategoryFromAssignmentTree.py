"""
A script returning security categories from a Person's assignments.

Differences to the stock implementation:

*  if category is follow_up, we look for destination_project

* if category not strict, we return not only the category, but also all its parents
  (unless we say it is strict)
"""

from Products.ERP5Type.Log import log

category_list = []

person_module = context.portal_url.getPortalObject().getDefaultModule('Person')
# It is better to keep getObject(), in this script this
# prevent a very strange bug, sometimes without getObject the
# assignment is not found
person_object_list = [x.getObject() for x in person_module.searchFolder(portal_type='Person', reference=user_name)]

if len(person_object_list) != 1:
  if len(person_object_list) > 1:
    raise ConsistencyError("Error: There is more than one Person with reference '%s'" % user_name)
  else:
    # if a person_object was not found in the module, we do nothing more
    # this happens for example when a manager with no associated person object
    # creates a person_object for a new user
    return []

person_object = person_object_list[0]

# We look for valid assignments of this user
for assignment in person_object.contentValues(filter={'portal_type': 'Assignment'}):
  category_dict = {}
  if assignment.getValidationState() == 'open':
    try:
      for base_category in base_category_list:
        if base_category == 'follow_up':
          category_value = assignment.getDestinationProject()
        else:
          category_value = assignment.getProperty(base_category)
          #XXX the role is not aquire in the assignment get if from the user_object
          if base_category=='role' and category_value in (None, ''):
            category_value = person_object.getRole()

        if category_value not in (None, ''):
          if root: category_value=category_value.split('/')[0]
          category_dict[base_category] = category_value
        else:
          raise RuntimeError("Error: '%s' property is required in order to update person security group"  % (base_category))
      category_list.append(category_dict)
      # if not strict, we go up the hierarchy (because if you work in group/a/b/c, chances are you 
      # are working in group/a/b, too :)
      if not strict:
        grouplist = category_value.split('/')
        for i in range(1,len(grouplist)):
          cdict = category_dict.copy()
          cdict[base_category] = '/'.join(grouplist[:-i])
          category_list.append(cdict)
    except RuntimeError as e:
      log(str(e))

return category_list
