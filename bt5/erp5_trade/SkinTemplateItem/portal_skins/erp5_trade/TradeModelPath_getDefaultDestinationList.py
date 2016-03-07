category_list = []
for base_category in context.getDestinationArrowBaseCategoryList():
  category = movement.getDefaultAcquiredCategoryMembership(base_category, base=1)
  if category:
    category_list.append(category)

return category_list
