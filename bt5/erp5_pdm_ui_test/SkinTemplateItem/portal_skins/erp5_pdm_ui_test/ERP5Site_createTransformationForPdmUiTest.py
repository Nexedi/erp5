portal = context.getPortalObject()

# Create resources and transformations.
for product_id in (
    'erp5_pdm_ui_test_product_with_one_transformation',
    'erp5_pdm_ui_test_product_with_two_transformations',
    'erp5_pdm_ui_test_product_without_transformation',
  ):
  if getattr(portal.product_module, product_id, None) is None:
    portal.product_module.newContent(id=product_id, portal_type='Product')

for component_id in (
    'erp5_pdm_ui_test_component_with_one_transformation',
    'erp5_pdm_ui_test_component_with_two_transformations',
    'erp5_pdm_ui_test_component_without_transformation',
  ):
  if getattr(portal.component_module, component_id, None) is None:
    portal.component_module.newContent(id=component_id, portal_type='Component')


erp5_pdm_ui_test_transformation_1 = portal.transformation_module.newContent(
    portal_type='Transformation',
    id='erp5_pdm_ui_test_transformation_1',
    resource_value=portal.product_module.erp5_pdm_ui_test_product_with_two_transformations,
)
erp5_pdm_ui_test_transformation_1.newContent(
    portal_type='Transformation Transformed Resource',
    resource_value=portal.product_module.erp5_pdm_ui_test_product_with_one_transformation,
)
erp5_pdm_ui_test_transformation_1.newContent(
    portal_type='Transformation Transformed Resource',
    resource_value=portal.component_module.erp5_pdm_ui_test_component_with_one_transformation,
)
erp5_pdm_ui_test_transformation_1.newContent(
    portal_type='Transformation Transformed Resource',
    resource_value=portal.component_module.erp5_pdm_ui_test_component_with_two_transformations,
)

erp5_pdm_ui_test_transformation_2 = portal.transformation_module.newContent(
    portal_type='Transformation',
    id='erp5_pdm_ui_test_transformation_2',
    resource_value=portal.component_module.erp5_pdm_ui_test_component_with_two_transformations,
)
erp5_pdm_ui_test_transformation_2.newContent(
    portal_type='Transformation Transformed Resource',
    resource_value=portal.product_module.erp5_pdm_ui_test_product_with_two_transformations,
)

portal.transformation_module.newContent(
    portal_type='Transformation',
    id='erp5_pdm_ui_test_transformation_3',
)

return "Delivery Created."
