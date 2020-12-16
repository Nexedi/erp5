from erp5.component.module.DateUtils import getClosestDate

portal = context.getPortalObject()

delivery_portal_type_list = ["Purchase Packing List", "Sale Packing List"]
delivery_id_list = ["erp5_item_renderjs_ui_test_purchase_packing_list",
                    "erp5_item_renderjs_ui_test_sale_packing_list"]
item_id = "erp5_item_renderjs_ui_test_item"

source_value = portal.restrictedTraverse('organisation_module/erp5_item_renderjs_ui_test_source_node')
destination_value = portal.restrictedTraverse('organisation_module/erp5_item_renderjs_ui_test_destination_node')
resource_value = portal.restrictedTraverse('product_module/erp5_item_renderjs_ui_test_product')
specialise_value = portal.restrictedTraverse('business_process_module/erp5_item_renderjs_ui_test_business_process')

item = portal.item_module.newContent(
  portal_type="Item",
  id=item_id,
  title='%s_title' % item_id,
  reference='%s_reference' % item_id)

for delivery_portal_type, delivery_id in zip(delivery_portal_type_list,
                                             delivery_id_list):
  module = portal.getDefaultModule(delivery_portal_type)
  delivery = module.newContent(
    portal_type=delivery_portal_type,
    id=delivery_id,
    title='%s_title' % delivery_id,
    start_date=getClosestDate(precision='day'),
    source_value=source_value,
    source_section_value=source_value,
    destination_value=destination_value,
    destination_section_value=destination_value,
    specialise_value=specialise_value
  )

  delivery.newContent(
    portal_type='%s Line' %delivery_portal_type,
    title='%s_line_title' % delivery_id,
    resource_value=resource_value,
    quantity=1,
    aggregate_value=item
  )

  delivery.confirm()

return "Item and Packing Lists Created."
