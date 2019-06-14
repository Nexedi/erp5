portal = context.getPortalObject()

delivery_portal_type = "Sale Packing List"
delivery_id = "erp5_trade_renderjs_ui_test_delivery"

# Delete event
module = portal.getDefaultModule(delivery_portal_type)
if getattr(module, delivery_id, None) is not None:
  module.manage_delObjects([delivery_id])

return "Deleted Successfully."
