for content in context.contentValues(portal_type='Inventory Line'):
  context.deleteContent(content.getId())

context.calculating()


context.activate().Inventory_calculateProductStock()
if not batch_mode:
  message = context.Base_translateString("Product Stock is creating")
  context.Base_redirect('view',keep_items={'portal_status_message': message})
