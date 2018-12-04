from DateTime import DateTime

portal = context.getPortalObject()
order_portal_type = "Sale Order"
order_line_portal_type = "Sale Order Line"
delivery_portal_type = "Sale Packing List"
delivery_line_portal_type = "Sale Packing List Line"

delivery_id = "erp5_pdm_ui_test_delivery"
delivery_title = "erp5_pdm_ui_test_delivery_title"

source_node_id = "erp5_pdm_ui_test_source_node"
destination_node_id = "erp5_pdm_ui_test_destination_node"

resource_id = "erp5_pdm_ui_test_product"
business_process = 'business_process_module/erp5_default_business_process'

quantity = 1

# Create an order or a packing list
if state in ['planned', 'ordered']:
  module = portal.getDefaultModule(order_portal_type)
  order = module.newContent(
    portal_type=order_portal_type,
    id=delivery_id,
    title=delivery_title,
    source='organisation_module/%s' % source_node_id,
    source_section='organisation_module/%s' % source_node_id,
    destination='organisation_module/%s' % destination_node_id,
    destination_section='organisation_module/%s' % destination_node_id,
    specialise=business_process,
    start_date=DateTime(),
  )
  order_line = order.newContent(
    portal_type=order_line_portal_type,
    resource='product_module/%s' % resource_id,
    quantity=1,
  )
  order.portal_workflow.doActionFor(order, 'plan_action')
  if state == 'ordered':
    order.portal_workflow.doActionFor(order, 'order_action')
  delivery = order

else:
  module = portal.getDefaultModule(delivery_portal_type)
  delivery = module.newContent(
    portal_type=delivery_portal_type,
    id=delivery_id,
    title=delivery_title,
    source='organisation_module/%s' % source_node_id,
    source_section='organisation_module/%s' % source_node_id,
    destination='organisation_module/%s' % destination_node_id,
    destination_section='organisation_module/%s' % destination_node_id,
    specialise=business_process,
    start_date=DateTime(),
  )
  delivery_line = delivery.newContent(
    portal_type=delivery_line_portal_type,
    resource='product_module/%s' % resource_id,
    quantity=1,
  )
  for next_state, transition in [
#     ('draft', 'confirm_action'),
#     ('confirmed', 'set_ready_action'),
#     ('ready', 'start_action'),
#     ('start', 'stop_action'),
#     ('stopped', 'deliver_action'),
    ('draft', 'confirm'),
    ('confirmed', 'setReady'),
    ('ready', 'start'),
    ('started', 'stop'),
    ('stopped', 'deliver'),
  ]:
    if state != next_state:
#       delivery.portal_workflow.doActionFor(delivery, transition)
      getattr(delivery, transition)()
    else:
      break

if delivery.getSimulationState() != state:
  raise ImplementationError, 'Delivery state is %s and not %s' % (delivery.getSimulationState(), state)

return "Delivery Created."

# vim: syntax=python
