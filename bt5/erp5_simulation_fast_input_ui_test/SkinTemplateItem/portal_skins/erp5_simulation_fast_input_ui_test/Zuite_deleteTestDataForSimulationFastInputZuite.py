portal = context.getPortalObject()

object_value_list = [
  getattr(portal.portal_rules, 'order_simulation_rule_for_simulation_fast_input_test', None),
  getattr(portal.portal_rules, 'delivery_simulation_rule_for_simulation_fast_input_test', None),
  getattr(portal.portal_deliveries, 'sale_packing_list_builder_for_simulation_fast_input', None),
  getattr(portal.business_process_module, 'business_process_for_simulation_fast_input', None),
  getattr(portal.sale_trade_condition_module, 'sale_trade_condition_for_simulation_fast_input', None),
  getattr(portal.product_module, 'product_for_simulation_fast_input', None),
  getattr(portal.sale_order_module, 'sale_order_for_simulation_fast_input', None),
]

for object_value in object_value_list:
  if object_value is None:
    continue
  object_value.getParentValue().manage_delObjects(ids=[object_value.getId()])

return "Deleted Successfully."
