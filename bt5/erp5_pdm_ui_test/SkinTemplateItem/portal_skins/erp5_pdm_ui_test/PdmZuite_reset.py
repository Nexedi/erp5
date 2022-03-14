portal = context.getPortalObject()

node_portal_type = "Organisation"
site_portal_type = "Category"
source_node_id = "erp5_pdm_ui_test_source_node"
source_node_title = "erp5_pdm_ui_test_source_node_title"
destination_node_id = "erp5_pdm_ui_test_destination_node"
destination_node_title = "erp5_pdm_ui_test_destination_node_title"
source_site_id = "erp5_pdm_ui_test_source_site"
source_site_title = "erp5_pdm_ui_test_source_site_title"
destination_site_id = "erp5_pdm_ui_test_destination_site"
destination_site_title = "erp5_pdm_ui_test_destination_site_title"


# validate rules
for rule in portal.portal_rules.objectValues():
  if rule.getValidationState() != 'validated':
    rule.validate()

# create categories
quantity_unit_category = portal.portal_categories.quantity_unit
if getattr(quantity_unit_category, "unit", None) is None:
  quantity_unit_category.newContent(
    portal_type="Category",
    id="unit",
    title="Unit",
  )
if getattr(quantity_unit_category.unit, "piece", None) is None:
  quantity_unit_category.unit.newContent(
    portal_type="Category",
    id="piece",
    title="Piece",
  )
if getattr(quantity_unit_category, "mass", None) is None:
  quantity_unit_category.newContent(
    portal_type="Category",
    id="mass",
    title="Mass",
  )
if getattr(quantity_unit_category.mass, "kilogram", None) is None:
  quantity_unit_category.mass.newContent(
    portal_type="Category",
    id="kilogram",
    title="Kilogram",
  )
if getattr(quantity_unit_category.mass, "ton", None) is None:
  quantity_unit_category.mass.newContent(
    portal_type="Category",
    id="ton",
    title="Ton",
  )

metric_type_category = portal.portal_categories.metric_type
if getattr(metric_type_category, "unit", None) is None:
  metric_type_category.newContent(
    portal_type="Category",
    id="unit",
    title="Unit",
  )
if getattr(metric_type_category.unit, "abstract_unit", None) is None:
  metric_type_category.unit.newContent(
    portal_type="Category",
    id="abstract_unit",
    title="Abstract Unit",
  )
if getattr(metric_type_category, "mass", None) is None:
  metric_type_category.newContent(
    portal_type="Category",
    id="mass",
    title="Mass",
  )

# create default quantity unit conversion groups
if getattr(portal.quantity_unit_conversion_module, 'unit_conversion_group', None) is None:
  portal.quantity_unit_conversion_module.newContent(
      portal_type='Quantity Unit Conversion Group',
      id='unit_conversion_group',
      quantity_unit_value=quantity_unit_category.unit.piece,
  ).validate()
# XXX we need a 1=1 for unit, because there's no other unit definition in this group
if getattr(portal.quantity_unit_conversion_module.unit_conversion_group, 'unit', None) is None:
  portal.quantity_unit_conversion_module.unit_conversion_group.newContent(
      portal_type='Quantity Unit Conversion Definition',
      id='unit',
      quantity_unit_value=quantity_unit_category.unit.piece,
      quantity=1,
  ).validate()
if getattr(portal.quantity_unit_conversion_module, 'mass_conversion_group', None) is None:
  portal.quantity_unit_conversion_module.newContent(
      portal_type='Quantity Unit Conversion Group',
      id='mass_conversion_group',
      quantity_unit_value=quantity_unit_category.mass.kilogram,
  ).validate()
if getattr(portal.quantity_unit_conversion_module.mass_conversion_group, 'ton', None) is None:
  portal.quantity_unit_conversion_module.mass_conversion_group.newContent(
      portal_type='Quantity Unit Conversion Definition',
      id='ton',
      quantity_unit_value=quantity_unit_category.mass.ton,
      quantity=1000,
  ).validate()
  # unit conversions are cached, so reset cache if we changed them
  portal.portal_caches.clearCacheFactory(('erp5_content_long', ))

# Create resources
portal.product_module.newContent(
  portal_type='Product',
  id='erp5_pdm_ui_test_product',
  title='erp5_pdm_ui_test_product_title',
  quantity_unit_value=quantity_unit_category.unit.piece,
).validate()
portal.product_module.erp5_pdm_ui_test_product.newContent(
  portal_type='Measure',
  metric_type_value=metric_type_category.mass,
  quantity_unit_value=quantity_unit_category.mass.kilogram,
  quantity=1500,
)
portal.product_module.erp5_pdm_ui_test_product.newContent(
  portal_type='Measure',
  metric_type_value=metric_type_category.unit.abstract_unit,
  quantity_unit_value=quantity_unit_category.unit.piece,
  quantity=3,
)
portal.component_module.newContent(
  portal_type='Component',
  id='erp5_pdm_ui_test_component',
  title='erp5_pdm_ui_test_component_title',
  quantity_unit_value=quantity_unit_category.unit.piece,
).validate()


# Create site categories
base_category = portal.restrictedTraverse('portal_categories/site')
for site_id, site_title in ((source_site_id, source_site_title),
                (destination_site_id, destination_site_title)):
  base_category.newContent(
    portal_type=site_portal_type,
    id=site_id,
    title=site_title
  )

# configure preference
portal.portal_preferences.getActivePreference().setPreferredNodeCategory(
    'site/' + destination_site_id if set_node_category_preference else None
)

# Create nodes
for node_id, node_title, site_url in ((source_node_id, source_node_title, source_site_id),
                          (destination_node_id, destination_node_title, destination_site_id)):
  module = portal.getDefaultModule(node_portal_type)
  module.newContent(
    portal_type=node_portal_type,
    id=node_id,
    title=node_title,
    site=site_url
  )

# Create supplies
# for all type of supply, source_node_id has 2 related supplies and destination_node_id has 1
for supply_portal_type in ('Purchase Supply', 'Sale Supply', 'Internal Supply', ):
  module = portal.getDefaultModule(supply_portal_type)
  module.newContent(
      portal_type=supply_portal_type,
      id='erp5_pdm_ui_test_supply_1',
      source_value=portal.organisation_module[source_node_id],
      destination_value=portal.organisation_module[destination_node_id],
  )
  module.newContent(
      portal_type=supply_portal_type,
      id='erp5_pdm_ui_test_supply_2',
      source_section_value=portal.organisation_module[source_node_id],
  )
  # an unrelated supply that should not be displayed
  module.newContent(
      portal_type=supply_portal_type,
      id='erp5_pdm_ui_test_supply_3',
  )


# Reset selections
stool = context.getPortalObject().portal_selections
stool.setSelectionFor('resource_current_inventory', None)
stool.setSelectionFor('movement_selection', None)

return "Reset Successfully."
