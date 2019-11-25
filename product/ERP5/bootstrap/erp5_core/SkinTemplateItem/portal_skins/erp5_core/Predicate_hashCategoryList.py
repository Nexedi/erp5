"""
  This script is used in parallel list fields in Predicate_view
"""
if default_sub_field_property_dict is None:
  default_sub_field_property_dict = {}
# Initialise result
sub_field_list = []

# use MultiListField
default_sub_field_property_dict.update({'field_type':'MultiListField'})

z = 0
category_list = []
for x in item_list:
  base_category = x[1].split('/', 1)[0]
  if base_category and base_category not in category_list:
    category_list.append(base_category)

for category in category_list:
  new_dict = default_sub_field_property_dict.copy()
  new_dict['value'] = [x for x in value_list if x.startswith('%s/' % category)]
  if z == 0:
    new_dict['title'] = '%s (%s)' % (default_sub_field_property_dict['title'], category)
  else:
    new_dict['title'] = '(%s)' % category
  new_dict['item_list'] = [['', '']] + [x for x in item_list if x[1].startswith('%s/' % category)]
  new_dict['key'] = str(z)
  if len(new_dict['item_list']) == 1:
    continue
  z += 1
  sub_field_list.append(new_dict)

return sub_field_list
