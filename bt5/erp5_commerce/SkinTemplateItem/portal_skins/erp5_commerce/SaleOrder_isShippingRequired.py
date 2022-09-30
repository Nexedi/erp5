'''
If all product have no Weight, it don't need to be sheep.
'''
return False
shopping_cart_items = context.SaleOrder_getShoppingCartItemList()

weight = 0
for order_line in shopping_cart_items:
  resource = order_line.getResourceValue()
  weight  += resource.getBaseWeight(0)

return weight > 0
