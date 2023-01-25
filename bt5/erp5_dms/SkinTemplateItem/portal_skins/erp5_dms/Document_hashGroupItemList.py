"""
  This script repeats function category items
  in such way that it is possible to select multiple
  function categories for the same document
"""
if default_sub_field_property_dict is None:
  default_sub_field_property_dict = {}
# Initialise result
sub_field_list = []

# Maximum size of the MultiListField
default_sub_field_property_dict.update({
  'required': 0,
  'field_type': 'ListField',
  'size': 1,
  'item_list': [('', '')] + item_list,
  'value': None,
})

z = 0
for _ in range(1):
  new_dict = default_sub_field_property_dict.copy()
  new_dict['title'] = '&nbsp;'
  new_dict['key'] = str(z)
  z += 1
  sub_field_list.append(new_dict)

# WARNING This code is very dangerous and ad hoc
# But it was the only way to make parallel list field
# work in this case
section_list = context.aq_parent.aq_parent.getGroupList()
section_list.reverse()
for value in section_list:
  new_dict = default_sub_field_property_dict.copy()
  new_dict['value'] = value
  new_dict['title'] = '&nbsp;'
  new_dict['key'] = str(z)
  z += 1
  sub_field_list.append(new_dict)

new_dict['title'] = default_sub_field_property_dict['title']
sub_field_list.reverse()
return sub_field_list
