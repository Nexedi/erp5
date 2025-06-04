portal = context.getPortalObject()

# Create Rules
order_rule = portal.portal_rules.newContent(
  portal_type='Order Root Simulation Rule',
  id='order_simulation_rule_for_simulation_fast_input_test',
  reference='order_simulation_rule_for_simulation_fast_input_test',
  version='1',
  trade_phase_value=portal.portal_categories.trade_phase.trade.order,
  test_method_id='Rule_testFalse')
order_rule.newContent(
  portal_type='Category Membership Divergence Tester',
  id='delivery_tester',
  updating_provider=True,
  divergence_provider=False,
  matching_provider=True,
  tested_property='delivery')
order_rule.newContent(
  portal_type='Float Divergence Tester',
  id='quantity_tester',
  updating_provider=True,
  divergence_provider=False,
  matching_provider=False,
  tested_property='quantity')
order_rule.newContent(
  portal_type='Category Membership Divergence Tester',
  id='resource_tester',
  updating_provider=True,
  divergence_provider=False,
  matching_provider=False,
  tested_property='resource')
order_rule.newContent(
  portal_type='Category Membership Divergence Tester',
  id='specialise_tester',
  updating_provider=True,
  divergence_provider=False,
  matching_provider=False,
  tested_property='specialise')
order_rule.newContent(
  portal_type='DateTime Divergence Tester',
  id='start_date_tester',
  updating_provider=True,
  divergence_provider=False,
  matching_provider=False,
  tested_property='start_date')
order_rule.newContent(
  portal_type='DateTime Divergence Tester',
  id='stop_date_tester',
  updating_provider=True,
  divergence_provider=False,
  matching_provider=False,
  tested_property='stop_date')
order_rule.validate()

delivery_rule = portal.portal_rules.newContent(
  portal_type='Delivery Simulation Rule',
  id='delivery_simulation_rule_for_simulation_fast_input_test',
  reference='delivery_simulation_rule_for_simulation_fast_input_test',
  version='1',
  trade_phase_value=portal.portal_categories.trade_phase.trade.delivery,
  test_method_id='SimulationMovement_testDeliverySimulationRuleForSimulationFastInput')
delivery_rule.newContent(
  portal_type='Float Divergence Tester',
  id='quantity_tester',
  updating_provider=True,
  divergence_provider=True,
  matching_provider=False,
  tested_property='quantity',
  solver_value=portal.portal_solvers['Quantity Split Solver'])
delivery_rule.newContent(
  portal_type='Category Membership Divergence Tester',
  id='resource_tester',
  updating_provider=True,
  divergence_provider=False,
  matching_provider=False,
  tested_property='resource')
delivery_rule.newContent(
  portal_type='DateTime Divergence Tester',
  id='start_date_tester',
  updating_provider=True,
  divergence_provider=False,
  matching_provider=False,
  tested_property='start_date')
delivery_rule.newContent(
  portal_type='DateTime Divergence Tester',
  id='stop_date_tester',
  updating_provider=True,
  divergence_provider=False,
  matching_provider=False,
  tested_property='stop_date')
delivery_rule.validate()

# Create Delivery Builder
builder = portal.portal_deliveries.newContent(
  portal_type='Delivery Builder',
  id='sale_packing_list_builder_for_simulation_fast_input',
  simulation_select_method_id='DeliveryBuilder_selectSalePackingListSimulationMovementList',
  delivery_module='sale_packing_list_module',
  delivery_portal_type='Sale Packing List',
  delivery_line_portal_type='Sale Packing List Line',
  delivery_cell_portal_type='Sale Packing List Line',
  delivery_after_generation_script_id='Base_updateSalePackingListAfterBuildingForSimulationFastInput',
  delivery_creatable=True)
builder.newContent(
  portal_type='Property Movement Group',
  id='property_movement_group_on_delivery',
  collect_order_group_value=portal.portal_categories.collect_order_group.delivery,
  int_index=1,
  tested_property_list=('stop_date', 'start_date'),
  divergence_scope_value=portal.portal_categories.divergence_scope.property)
builder.newContent(
  portal_type='Category Movement Group',
  id='category_movement_group_on_line',
  collect_order_group_value=portal.portal_categories.collect_order_group.line,
  int_index=1,
  tested_property_list=('resource',),
  divergence_scope_value=portal.portal_categories.divergence_scope.category)

# Create Business Process
business_process = portal.business_process_module.newContent(
  portal_type='Business Process',
  id='business_process_for_simulation_fast_input',
  reference='business_process_for_simulation_fast_input',
  version='1')
business_process.newContent(
  portal_type='Business Link',
  id='order',
  completed_state_list=('confirmed',),
  trade_phase_value=portal.portal_categories.trade_phase.trade.order,
  int_index=0,
  successor_value=portal.portal_categories.trade_state.ordered)
business_process.newContent(
  portal_type='Business Link',
  id='delivery',
  completed_state_list=('delivered',),
  predecessor_value=portal.portal_categories.trade_state.ordered,
  trade_phase_value=portal.portal_categories.trade_phase.trade.delivery,
  int_index=1,
  frozen_state_list=('delivered', 'stopped'),
  successor_value=portal.portal_categories.trade_state.delivered,
  delivery_builder_value=portal.portal_deliveries.sale_packing_list_builder_for_simulation_fast_input)
business_process.newContent(
  portal_type='Trade Model Path',
  id='order_path',
  title='Order',
  int_index=1,
  reference='TMP-ORDER',
  trade_phase_value=portal.portal_categories.trade_phase.trade.order)
business_process.newContent(
  portal_type='Trade Model Path',
  id='delivery_path',
  title='Delivery',
  int_index=2,
  reference='TMP-DELIVERY',
  trade_phase_value=portal.portal_categories.trade_phase.trade.delivery,
  payment_term=10,
  trade_date_value=portal.portal_categories.trade_phase.trade.order,
  payment_additional_term=10,
  )
business_process.validate()

# Create Sale Trade Condition
trade_condition = portal.sale_trade_condition_module.newContent(
  portal_type='Sale Trade Condition',
  id='sale_trade_condition_for_simulation_fast_input',
  specialise_value=portal.business_process_module.business_process_for_simulation_fast_input)
trade_condition.validate()

# Create Product
product = portal.product_module.newContent(
  portal_type='Product',
  id='product_for_simulation_fast_input')

# Sale Order
order = portal.sale_order_module.newContent(
  portal_type='Sale Order',
  id='sale_order_for_simulation_fast_input',
  title='sale_order_for_simulation_fast_input',
  specialise_value=trade_condition)
order.newContent(portal_type='Sale Order Line',
                 resource_value=product,
                 quantity=123)

return 'Created Successfully.'
