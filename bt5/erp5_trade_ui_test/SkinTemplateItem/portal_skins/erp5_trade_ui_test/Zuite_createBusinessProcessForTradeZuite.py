portal = context.getPortalObject()

# Create trade states

if getattr(portal.portal_categories.trade_state, 'erp5_trade_ui_test_ts', None) is None:
  portal.portal_categories.trade_state.newContent(
      id='erp5_trade_ui_test_ts'
  )
  portal.portal_categories.trade_state.erp5_trade_ui_test_ts.newContent(
      id='delivered',
      title='Delivered'
  )
  portal.portal_categories.trade_state.erp5_trade_ui_test_ts.newContent(
      id='invoiced',
      title='Invoiced'
  )

test_trade_ui_test_client = portal.business_process_module.newContent(
  id='test_trade_ui_test_business_process')

test_trade_ui_test_client.newContent(
      portal_type='Business Link',
      completed_state_list=('delivered', 'stopped'),
      frozen_state_list=('delivered', 'stopped'),
      predecessor_value=None,
      successor_value=portal.portal_categories.trade_state.erp5_trade_ui_test_ts.delivered,
      trade_phase_value=portal.portal_categories.trade_phase.erp5_trade_renderjs_ui_test_tp.delivery,
      title='Deliver'
)
test_trade_ui_test_client.newContent(
      portal_type='Business Link',
      completed_state_list=('delivered', 'stopped'),
      frozen_state_list=('delivered', 'stopped'),
      predecessor_value=portal.portal_categories.trade_state.erp5_trade_ui_test_ts.delivered,
      successor_value=portal.portal_categories.trade_state.erp5_trade_ui_test_ts.invoiced,
      trade_phase_value=portal.portal_categories.trade_phase.erp5_trade_renderjs_ui_test_tp.invoicing,
      title='Invoice'
)
# XXX not sure we need such links
test_trade_ui_test_client.newContent(
      portal_type='Business Link',
      completed_state_list=('delivered', 'stopped'),
      frozen_state_list=('delivered', 'stopped'),
      predecessor_value=portal.portal_categories.trade_state.erp5_trade_ui_test_ts.invoiced,
      successor_value=None,
      trade_phase_value=portal.portal_categories.trade_phase.erp5_trade_renderjs_ui_test_tp.invoicing,
      title='Finish'
)


return "Data Created."
