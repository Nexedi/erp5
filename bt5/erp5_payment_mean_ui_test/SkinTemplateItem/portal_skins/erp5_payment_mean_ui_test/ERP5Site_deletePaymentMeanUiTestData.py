portal = context.getPortalObject()

for portal_type, document_id_list in (
  ('Organisation', ('erp5_payment_mean_ui_test_organisation', )),
  ('Payment Transaction Group', ('erp5_payment_mean_ui_test_payment_transaction_group',),),
  ('Payment Transaction', (
      'erp5_payment_mean_ui_test_incoming_payment',
      'erp5_payment_mean_ui_test_outgoing_payment',
      'erp5_payment_mean_ui_test_planned_outgoing_payment',
      'erp5_payment_mean_ui_test_confirmed_outgoing_payment',
      'erp5_payment_mean_ui_test_confirmed_not_consistent_outgoing_payment',
      'erp5_payment_mean_ui_test_second_outgoing_payment',
      'erp5_payment_mean_ui_test_wrong_payment_mode_outgoing_payment',
      'erp5_payment_mean_ui_test_wrong_currency_outgoing_payment',
  ),),
):
  module = portal.getDefaultModule(portal_type)
  for document_id in document_id_list:
    if getattr(module, document_id, None) is not None:
      module.manage_delObjects([document_id])


return "Deleted Successfully."
