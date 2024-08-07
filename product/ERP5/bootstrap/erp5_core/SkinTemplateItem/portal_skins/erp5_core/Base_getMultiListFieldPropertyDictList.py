from collections import OrderedDict
if default_sub_field_property_dict is None:
  default_sub_field_property_dict = {}

# Define a dictionary where we store the subfields to display.
sub_field_dict = OrderedDict()
split_depth = 1
# Maximum size of the MultiListField
maximum_list_size = 5
# Try to assign each item to a sub field.
for item in item_list:
  # Get value of the item
  item_value = item[int(not is_right_display)]

  # Hash key from item_value (the relative_url), so that different base categories
  # appear as multiple multi list fields.
  # The item_list can contain entries with None as relative_url, like when using
  # disable_node option of CMFCategory. This case is not supported by this script,
  # because heuristics to put the None entry in one or another subfield group
  # are not implemented here.
  if item_value is None:
    continue
  item_split = item_value.split('/')
  item_key = '/'.join(item_split[:split_depth])
  base_category = item_split[0]
  # Create a new subfield if necessary
  if item_key not in sub_field_dict:
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

return sorted(
  sub_field_dict.values(),
  key=lambda v: v['title'])
