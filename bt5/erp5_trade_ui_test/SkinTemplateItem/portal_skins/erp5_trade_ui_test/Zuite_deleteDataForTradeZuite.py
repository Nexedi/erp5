portal = context.getPortalObject()

object_value_list = [
  getattr(context.sale_order_module, 'erp5_trade_ui_test_sale_order_1', None)
] + [
  getattr(portal.getDefaultModule(portal_type), "erp5_trade_ui_test_trade_condition", None)
  for portal_type in ("Internal Trade Condition", "Purchase Trade Condition", "Sale Trade Condition")
]

for object_value in object_value_list:
  if object_value is None:
    continue
  try:
    object_value.getParentValue().manage_delObjects(ids=[object_value.getId()])
  except:
    pass
return "Deleted Successfully."
