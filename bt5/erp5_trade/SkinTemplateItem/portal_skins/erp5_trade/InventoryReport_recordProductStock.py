portal = context.getPortalObject()
getCurrentInventoryList = portal.portal_simulation.getCurrentInventoryList
getCurrentInventoryAssetPrice = portal.portal_simulation.getCurrentInventoryAssetPrice
newContent = context.newContent
section_uid = context.getDestinationSectionUid()
node_uid = context.getDestinationUid()
valuation_method = context.getValuationMethod()
at_date = context.getInventoryDate()

for i in getCurrentInventoryList(
  section_uid = section_uid,
  node_uid = node_uid,
  group_by_resource = 1,
  group_by_variation = 1,
  resourceType=portal.getPortalProductTypeList(),
  omit_simulation = True,
  at_date = at_date
  ):
  total_price =  getCurrentInventoryAssetPrice(
    section_uid = section_uid,
    node_uid = node_uid,
    valuation_method = valuation_method,
    variation_text = i.variation_text,
    resource_uid = i.resource_uid,
    at_date = at_date,
    is_accountable = 1
  ) or 0
  inventory_line = newContent(portal_type='Inventory Report Line')
  inventory_line.edit(
  resource = i.getResource(),
  total_price = total_price,
  variation_category_list = i.variation_text,
  total_quantity = i.total_quantity)
    

context.record()
