cell_range = []

# Get base category list
selected_base_category_list = context.getVariationBaseCategoryList()

# Generate cell range
for base_category in selected_base_category_list:
  if matrixbox==1:
    # XXX matrixbox is right_display (not as listfield)
    # => invert display and value in item
    cell_range.append(map(lambda x: (x[1], x[0]),
                          context.getVariationCategoryItemList(
                                 base_category_list=[base_category,],
                                 display_base_category=display_base_category,
                                 sort_id='id')))
  else:
    cell_range.append(
              context.getVariationCategoryList(
                                     base_category_list=[base_category,],
                                     sort_id='id'))

# Remove empty range
cell_range = [x for x in cell_range if x!=[]]
return cell_range
