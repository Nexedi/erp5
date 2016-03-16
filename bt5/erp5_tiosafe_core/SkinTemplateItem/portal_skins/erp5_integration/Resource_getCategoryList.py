""" Retrieve the category list of the resource. """

result_list = []
cat_tool = context.getPortalObject().portal_categories

# add to the list the shared variations
for variation in context.getVariationCategoryItemList(omit_individual_variation=0, base=1, display_id='title'):
  cat = cat_tool.restrictedTraverse(variation[1])
  if cat.getPortalType() == "Category":
    result_list.append(variation[1])
  else:
    result_list.append(cat.getVariationBaseCategory()+"/"+cat.getTitle())

# sort the result list to always build the same xml
result_list.sort()

return result_list
