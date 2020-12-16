#getVariationCategoryItemList
item_list = context.getVariationCategoryList()

stock_status_message = {
  'STOCK' : 'In Stock',
  'AVAILABLE': 'Available',
  'UNAVAILABLE': 'Sold Out'}

portal_categories = context.portal_categories
result = []
for item in item_list:
  stock_status = context.Resource_getInventoryStatus(variation=variation, category=item)
  context.log(item)
  title = "%s (%s)" % (portal_categories.restrictedTraverse(item).getTranslatedTitle(), context.Base_translateString(stock_status_message[stock_status]))
  result.append((title, item))
return result
