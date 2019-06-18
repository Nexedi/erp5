portal = context.getPortalObject()

delivery_portal_type_list = ["Purchase Packing List", "Sale Packing List"]
delivery_id_list = ["erp5_item_renderjs_ui_test_purchase_packing_list",
                    "erp5_item_renderjs_ui_test_sale_packing_list"]
item_id = "erp5_item_renderjs_ui_test_item"

# Delete documents
for delivery_portal_type, delivery_id in zip(delivery_portal_type_list,
                                             delivery_id_list):
  module = portal.getDefaultModule(delivery_portal_type)
  delivery = getattr(module, delivery_id, None)
  if delivery is not None:

    for linking_document in portal.portal_catalog(strict__any__uid=delivery.getUid()):
      linking_document.getParentValue().manage_delObjects([linking_document.getId()])
    module.manage_delObjects([delivery_id])

item = getattr(portal.item_module, item_id, None)
if item is not None:
  portal.item_module.manage_delObjects([item_id])

return "Deleted Successfully."
