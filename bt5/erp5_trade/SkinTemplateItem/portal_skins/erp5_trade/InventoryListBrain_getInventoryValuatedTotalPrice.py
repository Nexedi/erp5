# XXX set request `precision` for total price field if not already set
request = container.REQUEST
if request.get('precision') is None:
  currency_relative_url = context.Base_getCurrencyForSection(request['section_category'] or request['node_category'])
  request.set('precision', context.getQuantityPrecisionFromResource(currency_relative_url))


if inventory_valuation_method:
  assert inventory_valuation_method in ('default_purchase_price',)

brain = context
if inventory_valuation_method == 'default_purchase_price':
  # XXX this does not support variations
  default_purchase_price = brain.getResourceValue().getDefaultPurchaseSupplyLineBasePrice()
  if default_purchase_price is None:
    return None
  return brain.inventory * default_purchase_price
