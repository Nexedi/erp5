"""
  "STOCK": Means available in stock.
  "AVAILABLE": Not in stock, but it will be available soon.
  "UNAVAILABLE": Not in stock neither to arrive.
"""
node_uid = [x.getUid() for x in context.getSpecialiseValueList()]

kw = {"resource_uid": context.getUid(),
      "node_uid":node_uid}

if variation:
  product, variation_id = variation.rsplit('/', 1)
  if product != context.getRelativeUrl():
    return "UNAVAILABLE"  # "WRONG VARIATION"

  if variation_id not in context.objectIds():
    return "UNAVAILABLE"  # "WRONG VARIATION"

  variation_list = []
  for base_category in context.getVariationBaseCategoryList():
    if base_category == 'variation':
      variation_list.append("%s/%s" % (base_category, variation))
    elif category is not None and category.startswith(base_category):
      variation_list.append(category)
    else:
      # For now we ignore all other kinds of variation.
      variation_list.append("%s/%%" % (base_category))

  kw['variation_text'] = "\n".join(variation_list)

current_inventory = context.portal_simulation.getCurrentInventory(**kw)

if current_inventory > 0:
  return "STOCK"

future_inventory = context.portal_simulation.getFutureInventory(**kw)

if future_inventory > 0:
  return "AVAILABLE"
return "UNAVAILABLE"
