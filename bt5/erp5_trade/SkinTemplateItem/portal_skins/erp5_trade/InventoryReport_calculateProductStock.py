for content in context.contentValues(portal_type='Inventory Report Line'):
  context.deleteContent(content.getId())
context.setTotalAssetPrice(0)
context.calculate()


context.activate().InventoryReport_recordProductStock()
if not batch_mode:
  message = context.Base_translateString("Product Stock is creating")
  return context.Base_redirect('view',keep_items={'portal_status_message': message})
