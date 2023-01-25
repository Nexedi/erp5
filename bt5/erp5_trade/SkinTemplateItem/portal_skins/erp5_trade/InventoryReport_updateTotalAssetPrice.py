total_asset_price = 0
for inventory_report_line in context.contentValues(portal_type='Inventory Report Line'):
  total_asset_price += inventory_report_line.total_asset_price

context.edit(
  total_asset_price = total_asset_price)
