request = container.REQUEST
portal = context.getPortalObject()

# set request `precision` for listbox's total price field if not already set
if request.get('precision') is None:
  request.set('precision', 3)   # fallback value to search only once if nothing is defined
  # Search an organisation's accounting currency to display currencies in this precision.
  organisation_search_kw = {
    'portal_type': 'Organisation',
  }
  if request.get('section_category'):
    organisation_search_kw['uid'] = portal.Base_getSectionUidListForSectionCategory(request['section_category'])
  else:
    organisation_search_kw['site_uid'] = portal.portal_categories.restrictedTraverse(request['node_category']).getUid()
  for brain in portal.portal_catalog(**organisation_search_kw):
    currency_relative_url = brain.getObject().getPriceCurrency()
    if currency_relative_url:
      request.set('precision', context.getQuantityPrecisionFromResource(currency_relative_url))
      break

def getPriceFromDefaultSupplyLine(brain, supply_line_id):
  # TODO: support variations ? (at same time this approach is intentionally super simple)
  # XXX what if this supply line's currency does not match the default accounting currency ?
  resource = brain.getResourceValue()

  base_price = None
  supply_line = getattr(resource, supply_line_id, None)
  if supply_line is not None:
    base_price = supply_line.getBasePrice()
    priced_quantity = supply_line.getPricedQuantity()
    if priced_quantity and supply_line.getQuantityUnit():
      priced_quantity = resource.convertQuantity(
        priced_quantity,
        supply_line.getQuantityUnit(),
        resource.getQuantityUnit())
    if base_price is not None:
      base_price /= priced_quantity
  if base_price is None:
    return None
  return brain.inventory * base_price

if inventory_valuation_method:
  supply_line_id_mapping = {
      'default_purchase_price': 'default_psl',
      'default_internal_price': 'default_isl',
      'default_sale_price': 'default_ssl',
  }
  return getPriceFromDefaultSupplyLine(
      context,
      supply_line_id_mapping[inventory_valuation_method],
  )
