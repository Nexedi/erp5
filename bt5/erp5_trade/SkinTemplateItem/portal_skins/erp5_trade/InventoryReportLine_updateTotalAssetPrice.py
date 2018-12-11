line_total_asset_price = context.getPortalObject().portal_simulation.getCurrentInventoryAssetPrice(**kw) or 0
context.edit(
  total_asset_price = context.getPortalObject().portal_simulation.getCurrentInventoryAssetPrice(**kw) or 0
  )
inventory_report = context.getParent()
inventory_report.edit(
  total_asset_price = inventory_report.getTotalAssetPrice() + line_total_asset_price)
