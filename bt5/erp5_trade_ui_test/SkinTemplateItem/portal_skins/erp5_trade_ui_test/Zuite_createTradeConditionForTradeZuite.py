from DateTime import DateTime

portal = context.getPortalObject()
trade_condition_portal_type = "%s Trade Condition" % delivery_type
supply_line_portal_type = "%s Supply Line" % delivery_type

trade_condition_id = "erp5_trade_ui_test_trade_condition"
trade_condition_title = "erp5_trade_ui_test_trade_condition_title"

resource_id = "erp5_pdm_ui_test_product"

delivery_portal_type = "%s Packing List" % delivery_type

# Create Trade Condition
module = portal.getDefaultModule(trade_condition_portal_type)
trade_condition = module.newContent(
  portal_type=trade_condition_portal_type,
  id=trade_condition_id,
  title=trade_condition_title,
)
trade_condition.newContent(
  portal_type=supply_line_portal_type,
  resource="product_module/" + resource_id
)

trade_condition.validate()

# Set it as specialise to the Delivery created by PdmZuite_createDelivery
module = portal.getDefaultModule(delivery_portal_type)
delivery = getattr(module, "erp5_pdm_ui_test_delivery", None)
if delivery is not None:
  delivery.setSpecialiseValue(trade_condition)
else:
  raise ValueError('Delivery not found')

return trade_condition_portal_type + " Created."
