'''
  return a list of slice items
'''
translateString = context.Base_translateString

# get the model the related model (usefull to get slice values). This script
# can be called on paysheet model line or on paysheet.
model = context.getParentValue().getPortalType()=='Pay Sheet Model' and\
          context.getParentValue() or context.getSpecialiseValue()

def framing(cell, name):
  '''
    this function return a string corresponding to the framing of the slice
    with the min and max value of the cell.
    e.g. : '2682.0 <= Tranche B < 10728'
  '''
  if cell is None:
    # This error happens when the cell is not found in the parent model or any
    # inherited model.
    return "%s (%s)" % (name, translateString('slice not defined'))

  return '%s <= %s < %s' % (cell.getQuantityRangeMin(),
                            name,
                            cell.getQuantityRangeMax())

resource = context.getResourceValue()
cell_range = []

if matrixbox :
  if resource is not None:
    base_category_list = context.getVariationBaseCategoryList()
    base_category_list.sort()
    for base_category in base_category_list:
      category_cell_range = []
      category_item_list = context.getVariationCategoryItemList(base_category_list = (base_category,),
                                                                display_id='translated_logical_path',
                                                                checked_permission='View')
      for category_item in category_item_list:
        if base_category == 'salary_range':
          category_cell_range.append((category_item[1],\
              framing(model.getCell(category_item[1]),
                      category_item[0])))
        elif base_category == 'contribution_share':
          category_cell_range.append((category_item[1],
            translateString('${contribution_share_title} (Amount or Percent)',
                            mapping=dict(contribution_share_title=category_item[0]))))
        else:
          raise ValueError(
            "%s: base category must be either contribution_share or salary_range"
            % script.id)
      cell_range.append(category_cell_range)

    cell_range = [x for x in cell_range if x]
  while len(cell_range) < 3:
    cell_range.append([])
  return cell_range
else:
  list_of_category_list = []
  variation_base_category_list = context.getVariationBaseCategoryList()
  variation_base_category_list.sort()
  for base_category in variation_base_category_list:
    if base_category == "base_application":
      base_application_variation_dict = {}
      variation_list = context.getVariationCategoryList(base_category_list=(base_category,))
      for variation in variation_list:
        # We split at the sublevel of base_application/base_amount/payroll/XXX
        base_variation = '/'.join(variation.split('/')[:4])
        base_application_variation_dict.setdefault(base_variation, [])
        base_application_variation_dict[base_variation].append(variation)

      for v in base_application_variation_dict.values():
        list_of_category_list.append(v)
    else:
      list_of_category_list.append(\
        context.getVariationCategoryList(base_category_list=base_category))
  return list_of_category_list

return []
