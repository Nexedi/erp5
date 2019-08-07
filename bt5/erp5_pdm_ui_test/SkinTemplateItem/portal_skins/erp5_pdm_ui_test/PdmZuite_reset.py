portal = context.getPortalObject()
self = context

resource_portal_type = "Product"
node_portal_type = "Organisation"
site_portal_type = "Category"
resource_id = "erp5_pdm_ui_test_product"
resource_title = "erp5_pdm_ui_test_product_title"
source_node_id = "erp5_pdm_ui_test_source_node"
source_node_title = "erp5_pdm_ui_test_source_node_title"
destination_node_id = "erp5_pdm_ui_test_destination_node"
destination_node_title = "erp5_pdm_ui_test_destination_node_title"
source_site_id = "erp5_pdm_ui_test_source_site"
source_site_title = "erp5_pdm_ui_test_source_site_title"
destination_site_id = "erp5_pdm_ui_test_destination_site"
destination_site_title = "erp5_pdm_ui_test_destination_site_title"

quantity_unit_category = portal.portal_categories.quantity_unit

# validate rules
for rule in portal.portal_rules.objectValues():
  if rule.getValidationState() != 'validated':
    rule.validate()

# Create resource
if getattr(quantity_unit_category, "unit", None) is None:
  quantity_unit_category.newContent(
    portal_type="Category",
    id="unit"
  )
module = portal.getDefaultModule(resource_portal_type)

resource = module.newContent(
  portal_type=resource_portal_type,
  id=resource_id,
  title=resource_title,
  quantity_unit='unit',
)
resource.validate()

# Create site categories
base_category = portal.restrictedTraverse('portal_categories/site')
for site_id, site_title in ((source_site_id, source_site_title),
                (destination_site_id, destination_site_title)):
  site = base_category.newContent(
    portal_type=site_portal_type,
    id=site_id,
    title=site_title
  )

# Create nodes
for node_id, node_title, site_url in ((source_node_id, source_node_title, source_site_id),
                          (destination_node_id, destination_node_title, destination_site_id)):
  module = portal.getDefaultModule(node_portal_type)
  node = module.newContent(
    portal_type=node_portal_type,
    id=node_id,
    title=node_title,
    site=site_url
  )

# Reset selections
stool = context.getPortalObject().portal_selections
stool.setSelectionFor('resource_current_inventory', None)
stool.setSelectionFor('movement_selection', None)

return "Reset Successfully."
