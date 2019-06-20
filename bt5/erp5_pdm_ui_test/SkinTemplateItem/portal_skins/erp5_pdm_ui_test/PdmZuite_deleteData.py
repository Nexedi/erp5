portal = context.getPortalObject()

resource_portal_type = "Product"
node_portal_type = "Organisation"
site_portal_type = "Category"

resource_id = "erp5_pdm_ui_test_product"

source_node_id = "erp5_pdm_ui_test_source_node"
destination_node_id = "erp5_pdm_ui_test_destination_node"

source_site_id = "erp5_pdm_ui_test_source_site"
destination_site_id = "erp5_pdm_ui_test_destination_site"

delivery_id = "erp5_pdm_ui_test_delivery"

# Delete resource
module = portal.getDefaultModule(resource_portal_type)
if getattr(module, resource_id, None) is not None:
  module.manage_delObjects([resource_id])

# Delete nodes
module = portal.getDefaultModule(node_portal_type)
for node_id in (source_node_id, destination_node_id):
  if getattr(module, node_id, None) is not None:
    module.manage_delObjects([node_id])

# Delete categories
base_category = portal.restrictedTraverse('portal_categories/site')
for site_id in (source_site_id, destination_site_id):
  if getattr(base_category, site_id, None) is not None:
    base_category.manage_delObjects([site_id])

stool = portal.portal_simulation
for delivery_type in ("Internal", "Purchase", "Sale"):
  order_portal_type = delivery_type + " Order"
  delivery_portal_type = delivery_type + " Packing List"

  # Delete order
  module = portal.getDefaultModule(order_portal_type)
  if getattr(module, delivery_id, None) is not None:
    delivery = getattr(module, delivery_id)
    stool.manage_delObjects(delivery.getCausalityRelatedIdList(portal_type='Applied Rule'))
    module.manage_delObjects([delivery_id])

  # Delete delivery
  module = portal.getDefaultModule(delivery_portal_type)
  if getattr(module, delivery_id, None) is not None:
    delivery = getattr(module, delivery_id)
    stool.manage_delObjects(delivery.getCausalityRelatedIdList(portal_type='Applied Rule'))
    module.manage_delObjects([delivery_id])

return "Deleted Successfully."
