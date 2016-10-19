resource = context.getResourceValue()
cell_range = []
if resource is not None:
  base_category_list = resource.getVariationBaseCategoryList()
  for base_category in base_category_list:
    if base_category == "base_application":
      base_application_variation_dict = {}
      variation_list = context.getVariationCategoryList(base_category_list=(base_category,))
      for variation in variation_list:
        # We split at the sublevel of base_application/base_amount/payroll/XXX
        base_variation = '/'.join(variation.split('/')[:4])
        base_application_variation_dict.setdefault(base_variation, []) 
        base_application_variation_dict[base_variation].append(variation)

      for v in base_application_variation_dict.values():
        if matrixbox == 1:
          cell_range.append(map(lambda x: (x[1],x[0]), v))
        else:
          cell_range.append(v)
    else:
      if matrixbox == 1:
        # XXX matrixbox is right_display (not as listfield) => invert display and value in item
        if context.getVariationCategoryList(base_category_list=(base_category,)):
          cell_range.append(map(lambda x: (x[1],x[0]),
            context.getVariationCategoryItemList(base_category_list=\
                (base_category,) ) ) )
      else:
        cell_range.append(context.getVariationCategoryList(base_category_list=\
            (base_category,)))

  cell_range = filter(lambda x: x != [], cell_range )

return cell_range
