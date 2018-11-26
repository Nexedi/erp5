for content in context.contentValues(portal_type='Inventory Line'):
  context.deleteContent(content.getId())

context.calculate()


context.activate().Inventory_recordProductStock()
if not batch_mode:
  message = context.Base_translateString("Product Stock is creating")
  context.Base_redirect('view',keep_items={'portal_status_message': message})
