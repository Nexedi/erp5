resource = context.getResourceValue()
cell_range = []
if resource is not None:
  base_category_list = resource.getVariationBaseCategoryList(
                                             omit_optional_variation=1)

  for base_category in base_category_list:
    if matrixbox == 1:
      # XXX matrixbox is right_display (not as listfield) => invert display and value in item
      cell_range.append( map(lambda x: (x[1],x[0]), context.getVariationCategoryItemList(base_category_list = (base_category,) ) ) )
    else:
      cell_range.append( context.getVariationCategoryList(base_category_list = (base_category,) ) )

  cell_range = filter(lambda x: x != [], cell_range )

return cell_range
