# base_id possible value: 'quantity', 'variation'

get_variation_base_category_method_dict = {
  'quantity': 'getQVariationBaseCategoryList',
  'variation': 'getVVariationBaseCategoryList'
}

cell_range = []
transformation = context.getParentValue()

# Those value are define on property sheet of portal type
line_base_category = transformation.getVariationBaseCategoryLine()
column_base_category = transformation.getVariationBaseCategoryColumn()

base_category_list = transformation.getVariationBaseCategoryList()
tab_base_category_list = filter(lambda x: x not in [line_base_category, 
                                     column_base_category], base_category_list)

for c in ([line_base_category, column_base_category] + tab_base_category_list):
  # try to display line first, then column, and finally others
  if c in getattr(context, 
                  get_variation_base_category_method_dict[base_id])():
    # base category was selected by user
    if matrixbox == 1:
      # XXX matrixbox is right_display (not as listfield) 
      # => invert display and value in item
      cell_range.append(map(lambda x: (x[1],x[0]), 
                        transformation.getVariationCategoryItemList
                                (base_category_list=(c,))))
    else:
      cell_range.append(transformation.getVariationCategoryList(
                                             base_category_list=(c,)))

# Remove empty range
cell_range = filter(lambda x: x != [], cell_range)

return cell_range
