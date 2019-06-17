portal = context.getPortalObject()

delivery_portal_type = "Sale Order"
delivery_id = "erp5_trade_renderjs_ui_test_order"

# Delete event
module = portal.getDefaultModule(delivery_portal_type)
delivery = getattr(module, delivery_id, None)
if delivery is not None:

  for linking_document in portal.portal_catalog(strict__any__uid=delivery.getUid()):
    linking_document.getParentValue().manage_delObjects([linking_document.getId()])
  module.manage_delObjects([delivery_id])

return "Deleted Successfully."
