portal = context.getPortalObject()

# Create organisations
erp5_trade_ui_test_organisation_1 = portal.organisation_module.newContent(
    portal_type='Organisation',
    id='erp5_trade_ui_test_organisation_1',
    title='erp5_trade_ui_test_organisation_1_title',
)
erp5_trade_ui_test_organisation_2 = portal.organisation_module.newContent(
    portal_type='Organisation',
    id='erp5_trade_ui_test_organisation_2',
    title='erp5_trade_ui_test_organisation_2_title',
)

# Create trade conditions
# for all type of trade condition, erp5_trade_ui_test_organisation_1 has 2 related supplies
# and erp5_trade_ui_test_organisation_2 has 1
for trade_condition_portal_type in (
    'Purchase Trade Condition',
    'Sale Trade Condition',
    'Internal Trade Condition', ):
  module = portal.getDefaultModule(trade_condition_portal_type)
  module.newContent(
      portal_type=trade_condition_portal_type,
      id='erp5_trade_ui_test_trade_condition_1',
      source_value=erp5_trade_ui_test_organisation_1,
      destination_value=erp5_trade_ui_test_organisation_2,
  )
  module.newContent(
      portal_type=trade_condition_portal_type,
      id='erp5_trade_ui_test_trade_condition_2',
      source_section_value=erp5_trade_ui_test_organisation_1,
  )
  # an unrelated trade_condition that should not be displayed
  module.newContent(
      portal_type=trade_condition_portal_type,
      id='erp5_trade_ui_test_trade_condition_3',
  )

return "Data Created."
