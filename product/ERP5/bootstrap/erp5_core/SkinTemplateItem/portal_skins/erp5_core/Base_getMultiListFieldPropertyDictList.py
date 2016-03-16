# Define a dictionary where we store the subfields to display.
sub_field_dict = {}
split_depth = 1
# Maximum size of the MultiListField
maximum_list_size = 5
# Try to assign each item to a sub field.
for item in item_list:
  # Get value of the item
  item_value = item[int(not is_right_display)]
  # Hash key from item_value
  item_split = item_value.split('/')
  item_key = '/'.join(item_split[:split_depth])
  base_category = item_split[0]
  # Create a new subfield if necessary
  if not sub_field_dict.has_key(item_key):
    # Create property dict (key are field parameters)
    sub_field_property_dict = default_sub_field_property_dict.copy()
    sub_field_property_dict['key'] = item_key
    sub_field_property_dict['title'] = context.portal_categories[base_category].getTitle()
    sub_field_property_dict['required'] = 0
    sub_field_property_dict['field_type'] = 'MultiListField'
    sub_field_property_dict['size'] = 1
    sub_field_property_dict['item_list'] = []
    sub_field_property_dict['value'] = []
    sub_field_dict[item_key] = sub_field_property_dict
  # Put the value in the correct sub field.
  sub_field_dict[item_key]['item_list'].append(item)
  sub_field_property_dict['size'] = min(len(sub_field_dict[item_key]['item_list']) , maximum_list_size )
  if item_value in value_list:
    sub_field_dict[item_key]['value'].append(item_value)

# Return the list of subfield configuration.

return sub_field_dict.values()
