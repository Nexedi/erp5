category_list = []
for base_category in context.getSourceArrowBaseCategoryList():
  category = context.getDefaultAcquiredCategoryMembership(base_category, base=1) # This should be moved to degault implementation of business path - XXX-JPS
  if category is None:
    category = movement.getDefaultAcquiredCategoryMembership(base_category, base=1)
  if category:
    category_list.append(category)

return category_list
