if inventory_valuation_method:
  assert inventory_valuation_method in ('default_purchase_price',)

brain = context
if inventory_valuation_method == 'default_purchase_price':
  return brain.inventory * (brain.getResourceValue().getDefaultPurchaseSupplyLineBasePrice() or 0)
