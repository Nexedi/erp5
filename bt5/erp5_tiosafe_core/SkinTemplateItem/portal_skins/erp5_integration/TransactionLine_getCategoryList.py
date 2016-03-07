category_list = []

# Add the variations list
for category in context.getVariationCategoryList():
  category_list.append(category)

# TODO: check if individual variations are take away
category_list.sort()

return category_list
