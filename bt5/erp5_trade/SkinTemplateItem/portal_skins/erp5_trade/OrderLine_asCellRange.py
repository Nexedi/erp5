resource = context.getResourceValue()
cell_range = []
if resource is not None:
  base_category_list = resource.getVariationBaseCategoryList(
                                          omit_optional_variation=1)

  for base_category in base_category_list:
    if matrixbox == 1:
      # XXX matrixbox is right_display (not as listfield) =>
      # invert display and value in item
      cell_range.append([(x[1], x[0]) for x in
                        context.getVariationCategoryItemList(
                                     base_category_list = (base_category,))])
    else:
      cell_range.append(context.getVariationCategoryList(\
                                 base_category_list=(base_category,)))

  cell_range = [x for x in cell_range if x != []]

return cell_range
