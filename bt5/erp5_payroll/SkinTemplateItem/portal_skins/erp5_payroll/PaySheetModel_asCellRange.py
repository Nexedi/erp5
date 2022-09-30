'''
  this script return a list of catorgory Items
  It's used in the Pay Sheet Model to return all category slices
  corresponding to childs of the selection of the base category in the view
'''

category_list = []

for category in context.getVariationSettingsCategoryList():
  category_name = category.replace('salary_range/','',1)
  if context.portal_categories.getCategoryValue(category) is None:
    raise ValueError('no category %s' % category)
  else:
    if matrixbox:
      category_list.extend(context.portal_categories.getCategoryValue(category).getCategoryChildLogicalPathItemList(checked_permission='View', is_right_display=1, base=1)[1:])
    else:
      cat_list = [cat[0] for cat in
          context.portal_categories.salary_range[category_name].getCategoryChildItemList(checked_permission='View', base=1)[1:]]
      category_list.append(cat_list)

return category_list
