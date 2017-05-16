variation_title = ""
variation_range_list = context.Item_getVariationRangeCategoryItemList()

for variation in context.Item_getVariationCategoryList():
  if variation.startswith("variation"):
    variation_title_list = [i[0] for i in variation_range_list if i[1] == variation]
    if len(variation_title_list):
      variation_title = variation_title_list[0]
      break

product_title = context.Item_getResourceTitle()

total = len(product_title) + 1 + len(variation_title)

return product_title[0:len(product_title)*24 / total ] +' ' +  variation_title[0:len(variation_title)*24 / total ]
