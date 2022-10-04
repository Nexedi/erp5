if default_sub_field_property_dict is None:
  default_sub_field_property_dict = {}
sub_field_dict = {}
split_depth = 1
resource = context.getResourceValue()
if resource is not None:
  not_option_base_category_list = resource.getVariationBaseCategoryList(
                                                 omit_optional_variation=1)
else :
  not_option_base_category_list = ()

del default_sub_field_property_dict['item_list']
for item in item_list:
  # Remove empty items
  if item in (('',''), ['','']):
    continue
  # Get value of the item
  item_value = item[int(not is_right_display)]
  # Hash key from item_value
  item_split = item_value.split('/')
  item_key = '/'.join(item_split[:split_depth])
  base_category = item_split[0]

  sub_field_property_dict = sub_field_dict.setdefault(item_key, default_sub_field_property_dict.copy())

  sub_field_property_dict['key'] = item_key
  sub_field_property_dict['required'] = int(base_category in not_option_base_category_list)
  sub_field_property_dict['field_type'] = 'ListField'
  sub_field_property_dict['size'] = 1
  sub_field_property_dict.setdefault('item_list', [('', '')]).extend([item])
  if item_value in value_list:
    # Only one value per variation
    sub_field_property_dict['value'] = item_value

return sub_field_dict.values()
