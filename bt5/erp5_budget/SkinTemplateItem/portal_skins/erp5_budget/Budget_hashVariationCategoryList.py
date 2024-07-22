if default_sub_field_property_dict is None:
  default_sub_field_property_dict = {}
# Remove empty items
item_list = [x for x in item_list if x not in (('',''), ['',''])]

sub_field_dict = {}
split_depth = 1

# Build a dict of title to display, based on the titles of corresponding
# budget variations, and a dict of indexes for sorting.
base_category_title_dict = {}
base_category_int_index_dict = {}
budget = container.REQUEST.get('here')
if budget is not None:
  budget_model =budget.getSpecialiseValue()
  if budget_model is not None:
    for budget_variation in budget_model.contentValues():
      if budget_variation.hasTitle():
        base_category_title_dict[
          budget_variation.getProperty('variation_base_category')
          ] =  budget_variation.getTranslatedTitle()
      base_category_int_index_dict[
          budget_variation.getProperty('variation_base_category')
          ] =  budget_variation.getIntIndex()

resolveCategory = context.getPortalObject().portal_categories.resolveCategory

for item in item_list:
  # Get value of the item
  item_value = item[int(not is_right_display)]

  # Hash key from item_value
  item_split = item_value.split('/')
  item_key = '/'.join(item_split[:split_depth])
  base_category = item_split[0]
  multi = False # XXX or now budget level are only single value.

  if item_key not in sub_field_dict:
    # Create property dict
    sub_field_property_dict = default_sub_field_property_dict.copy()
    sub_field_property_dict['key'] = item_key
    sub_field_property_dict['required'] = 0
    sub_field_property_dict['field_type'] = multi and 'MultiListField' or 'ListField'
    sub_field_property_dict['size'] = multi and 15 or 1
    sub_field_property_dict['item_list'] = [('','')]
    sub_field_property_dict['value'] = []
    sub_field_dict[item_key] = sub_field_property_dict

  sub_field_dict[item_key]['item_list'] =\
     sub_field_dict[item_key]['item_list'] + [item]

  if item_value in value_list:
    if multi:
      sub_field_dict[item_key]['value'] =\
        sub_field_dict[item_key]['value'] + [item_value]
    else:
      sub_field_dict[item_key]['value'] = item_value

  sub_field_dict[item_key]['int_index'] = base_category_int_index_dict.get(
                                                    base_category, -1)

  if base_category in base_category_title_dict:
    sub_field_dict[item_key]['title'] = base_category_title_dict[base_category]
  else:
    base_category_value = resolveCategory(base_category)
    if base_category_value is not None:
      sub_field_dict[item_key]['title'] = base_category_value.getTranslatedTitle()
    else:
      sub_field_dict[item_key]['title'] = base_category

return sorted(
  sub_field_dict.values(),
  key=lambda d: d['int_index']
)
