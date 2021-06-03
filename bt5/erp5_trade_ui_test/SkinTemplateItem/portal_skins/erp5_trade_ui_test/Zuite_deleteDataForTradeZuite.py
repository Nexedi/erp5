portal = context.getPortalObject()

object_value_list = [
  getattr(portal.sale_order_module, 'erp5_trade_ui_test_sale_order_1', None),
  getattr(portal.organisation_module, 'erp5_trade_ui_test_organisation_1', None),
  getattr(portal.organisation_module, 'erp5_trade_ui_test_organisation_2', None),
] + [
  getattr(portal.getDefaultModule(portal_type), "erp5_trade_ui_test_trade_condition" + suffix, None)
  for portal_type in ("Internal Trade Condition", "Purchase Trade Condition", "Sale Trade Condition")
  for suffix in ('', '_1', '_2', '_3')
]

for object_value in object_value_list:
  if object_value is None:
    continue
  object_value.getParentValue().manage_delObjects(ids=[object_value.getId()])

return "Deleted Successfully."
