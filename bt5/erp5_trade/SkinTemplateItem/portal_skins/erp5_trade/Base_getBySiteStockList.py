result_list = []
inventory_list_method_dict = {
  'current': 'getCurrentInventoryList',
  'future': 'getFutureInventoryList',
  'available': 'getAvailableInventoryList',
}

if section_category:
  kw['section_category'] = section_category

if product_line:
  kw['resource_category'] = product_line

for brain in getattr(context.portal_simulation, inventory_list_method_dict[simulation_period])(
    node_category=node_category,
    group_by_resource=True,
    group_by_variation=True,
    group_by_node=False,
    at_date=at_date,
    # resource_portal_type= does not work with cells (because resource is acquired from line)
    resourceType=context.getPortalProductTypeList(),
    **kw):

  if positive_stock and negative_stock and not zero_stock and brain.inventory == 0:
    result_list.append(brain)
  if positive_stock and not negative_stock and zero_stock and brain.inventory <0:
    result_list.append(brain)
  if negative_stock and zero_stock and not positive_stock and brain.inventory >0:
    result_list.append(brain)
  if positive_stock and not negative_stock and not zero_stock and brain.inventory <=0:
    result_list.append(brain)
  if negative_stock and not positive_stock and not zero_stock and brain.inventory >=0:
    result_list.append(brain)
  if zero_stock and not positive_stock and not negative_stock and brain.inventory!=0:
    result_list.append(brain)
  if not positive_stock and not negative_stock and not zero_stock:
    result_list.append(brain)

return sorted(result_list, key=lambda brain: (brain.getResourceReference(), brain.getResourceTitle(), brain.variation_text))
