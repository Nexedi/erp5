# Remove empty items
item_list = filter(lambda x: x not in [('',''), ['','']], 
                   item_list)

sub_field_dict = {}
split_depth = 1

for item in item_list:
  # Get value of the item
  item_value = item[int(not is_right_display)]
  
  # Hash key from item_value
  item_split = string.split(item_value, '/')
  item_key = string.join(item_split[:split_depth] , '/' )
  base_category = item_split[0]
  if not sub_field_dict.has_key(item_key):
    # Create property dict
    sub_field_property_dict = default_sub_field_property_dict.copy()
    sub_field_property_dict['key'] = item_key
    sub_field_property_dict['required'] = 1
    sub_field_property_dict['field_type'] = 'ListField'
    sub_field_property_dict['size'] = 1
    sub_field_property_dict['title'] = context.portal_categories[base_category].getTitle()
    sub_field_property_dict['item_list'] = [('','')]
    sub_field_dict[item_key] = sub_field_property_dict

  sub_field_dict[item_key]['item_list'] =\
     sub_field_dict[item_key]['item_list'] + [item]
  if item_value in value_list:
    sub_field_dict[item_key]['value'] = item_value

return sub_field_dict.values()
