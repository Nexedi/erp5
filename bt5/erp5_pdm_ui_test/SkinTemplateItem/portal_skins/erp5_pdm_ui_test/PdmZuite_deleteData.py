portal = context.getPortalObject()

node_portal_type = "Organisation"
source_node_id = "erp5_pdm_ui_test_source_node"
destination_node_id = "erp5_pdm_ui_test_destination_node"

source_site_id = "erp5_pdm_ui_test_source_site"
destination_site_id = "erp5_pdm_ui_test_destination_site"

delivery_id = "erp5_pdm_ui_test_delivery"

# Delete resources
for product_id in (
    'erp5_pdm_ui_test_product',
    'erp5_pdm_ui_test_product_with_two_transformations',
    'erp5_pdm_ui_test_product_without_transformation',
  ):
  if getattr(portal.product_module, product_id, None) is not None:
    portal.product_module.manage_delObjects([product_id])
for component_id in (
    'erp5_pdm_ui_test_component',
    'erp5_pdm_ui_test_component_with_two_transformations',
    'erp5_pdm_ui_test_component_without_transformation',
  ):
  if getattr(portal.component_module, component_id, None) is not None:
    portal.component_module.manage_delObjects([component_id])

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

# delete supplies
for supply_portal_type in ('Purchase Supply', 'Sale Supply', 'Internal Supply', ):
  module = portal.getDefaultModule(supply_portal_type)
  for supply_id in ('erp5_pdm_ui_test_supply_1', 'erp5_pdm_ui_test_supply_2', 'erp5_pdm_ui_test_supply_3'):
    if getattr(module, supply_id, None) is not None:
      module.manage_delObjects([supply_id])

for transformation_id in (
      'erp5_pdm_ui_test_transformation_1',
      'erp5_pdm_ui_test_transformation_2',
      'erp5_pdm_ui_test_transformation_3',
  ):
  if getattr(portal.transformation_module, transformation_id, None) is not None:
    portal.transformation_module.manage_delObjects([transformation_id])


# delete supplies
for supply_portal_type in ('Purchase Supply', 'Sale Supply', 'Internal Supply', ):
  module = portal.getDefaultModule(supply_portal_type)
  for supply_id in ('erp5_pdm_ui_test_supply_1', 'erp5_pdm_ui_test_supply_2', 'erp5_pdm_ui_test_supply_3'):
    if getattr(module, supply_id, None) is not None:
      module.manage_delObjects([supply_id])

return "Deleted Successfully."
