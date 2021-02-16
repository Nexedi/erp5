"""
Security categories assigned from the Person who is set as the destination
of the document (e.g. in Memo type).
"""
from erp5.component.module.Log import log
category_list = []

for ob in obj.getDestinationValueList():
  category_dict = {}
  for base_category in base_category_list:
    if base_category == 'group':
      category_value = ob.Person_getPrincipalGroup()
    else:
      category_value = ob.getProperty(base_category)
    if category_value not in (None, ''):
      category_dict[base_category] = category_value
    else:
      raise RuntimeError("Error: '%s' property is required in order to update person security group"  % base_category)
  category_list.append(category_dict)

log(category_list)
return category_list
