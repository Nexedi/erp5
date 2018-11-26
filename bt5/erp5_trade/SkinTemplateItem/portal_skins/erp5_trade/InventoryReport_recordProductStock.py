portal = context.getPortalObject()
getCurrentInventoryList = portal.portal_simulation.getCurrentInventoryList
newContent = context.newContent
section_uid = context.getDestinationSectionUid()
node_uid = context.getDestinationUid()
valuation_method = context.getValuationMethod()
relative_url = context.getRelativeUrl()
at_date = context.getAtDate()

inventory_list = getCurrentInventoryList(
  section_uid = section_uid,
  node_uid = node_uid,
  group_by_resource = 1,
  group_by_variation = 1,
  resourceType=portal.getPortalProductTypeList(),
  at_date = at_date
)

line_tag = '%s:lineUpdateTotalAssetPrice' % relative_url
#only after all calculation are finished then change report state
for inventory in inventory_list:
  inventory_report_line = newContent(portal_type='Inventory Report Line')
  inventory_report_line.edit(
    resource = inventory.getResource(),
    variation_category_list = inventory.variation_text,
    total_quantity = inventory.total_quantity,
    total_asset_price=0
  )
  inventory_report_line.activate(
    tag = line_tag
    ).InventoryReportLine_updateTotalAssetPrice(
      section_uid = section_uid,
      node_uid = node_uid,
      valuation_method = valuation_method,
      variation_text = inventory.variation_text,
      resource_uid = inventory.resource_uid,
      at_date = at_date,
      is_accountable = 1
    )

tag = '%s:updateTotalAssetPrice' % relative_url
context.activate(after_tag=line_tag, tag=tag).InventoryReport_updateTotalAssetPrice()
context.activate(after_tag=tag).record()
