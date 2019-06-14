from DateTime import DateTime

portal = context.getPortalObject()

delivery_portal_type = "Sale Packing List"
delivery_id = "erp5_trade_renderjs_ui_test_delivery"

source_value = portal.restrictedTraverse('organisation_module/erp5_trade_renderjs_ui_test_source_node')
destination_value = portal.restrictedTraverse('organisation_module/erp5_trade_renderjs_ui_test_destination_node')
specialise_value = portal.restrictedTraverse('business_process_module/erp5_trade_renderjs_ui_test_business_process')
resource_value = portal.restrictedTraverse('product_module/erp5_trade_renderjs_ui_test_product')

module = portal.getDefaultModule(delivery_portal_type)
delivery = module.newContent(
  portal_type=delivery_portal_type,
  id=delivery_id,
  title='%s_title' % delivery_id,
  start_date=DateTime(),
  source_value=source_value,
  source_section_value=source_value,
  destination_value=destination_value,
  destination_section_value=destination_value,
  specialise_value=specialise_value
)

delivery.newContent(
  portal_type='Sale Packing List Line',
  resource_value=resource_value
)

delivery.startBuilding()

return "Sale Packing List Created."
