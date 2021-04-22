from DateTime import DateTime

portal = context.getPortalObject()

# validate rules ( see Products.ERP5Type.tests.ERP5TypeTestCase )
for rule in portal.portal_rules.contentValues():
  if rule.getValidationState() != 'validated':
    rule.validate()

organisation_id = "erp5_payment_mean_ui_test_organisation"
organisation = portal.organisation_module.newContent(
    portal_type='Organisation',
    id=organisation_id,
    title=organisation_id,
    group_value=portal.portal_categories.group.demo_group,
)
bank_account_id = "erp5_payment_mean_bank"
bank_account = organisation.newContent(
    portal_type='Bank Account',
    id=bank_account_id,
    title=bank_account_id
)

payment_mean_id = "erp5_payment_mean_ui_test_payment_transaction_group"
payment_mean = portal.payment_transaction_group_module.newContent(
    portal_type="Payment Transaction Group",
    id=payment_mean_id,
    title=payment_mean_id,
    source_section_value=organisation,
    source_payment_value=bank_account,
    stop_date=DateTime('2019/10/21'),
    price_currency_value=portal.currency_module.euro,
    payment_mode_value=portal.portal_categories.payment_mode.cash,
    payment_transaction_group_type_value=portal.portal_categories.payment_transaction_group_type.outgoing,
)
payment_mean.open()

incoming_payment = portal.accounting_module.newContent(
    portal_type='Payment Transaction',
    id="erp5_payment_mean_ui_test_incoming_payment",
    title="Incoming payment",
    source_section_value=organisation,
    destination_section_value=organisation,
    source_payment_value=bank_account,
    start_date=DateTime('2019/10/20'),
    resource_value=portal.currency_module.euro,
    payment_mode_value=portal.portal_categories.payment_mode.cash,
    specialise_value=portal.business_process_module.erp5_default_business_process,
)
incoming_payment.bank.edit(
    source_value=portal.account_module.bank,
    source_debit=100,
)
incoming_payment.stop()

outgoing_payment = portal.accounting_module.newContent(
    portal_type='Payment Transaction',
    id="erp5_payment_mean_ui_test_outgoing_payment",
    title="Outgoing payment",
    source_section_value=organisation,
    destination_section_value=organisation,
    source_payment_value=bank_account,
    start_date=DateTime('2019/10/20'),
    resource_value=portal.currency_module.euro,
    payment_mode_value=portal.portal_categories.payment_mode.cash,
    specialise_value=portal.business_process_module.erp5_default_business_process,
)
outgoing_payment.bank.edit(
    source_value=portal.account_module.bank,
    source_credit=100,
)
outgoing_payment.stop()

second_outgoing_payment = portal.accounting_module.newContent(
    portal_type='Payment Transaction',
    id="erp5_payment_mean_ui_test_second_outgoing_payment",
    title="Second outgoing payment",
    source_section_value=organisation,
    destination_section_value=organisation,
    source_payment_value=bank_account,
    start_date=DateTime('2019/10/21'),
    resource_value=portal.currency_module.euro,
    payment_mode_value=portal.portal_categories.payment_mode.cash,
    specialise_value=portal.business_process_module.erp5_default_business_process,
)
second_outgoing_payment.bank.edit(
    source_value=portal.account_module.bank,
    source_credit=100,
)
second_outgoing_payment.stop()

wrong_payment_mode_outgoing_payment = portal.accounting_module.newContent(
    portal_type='Payment Transaction',
    id="erp5_payment_mean_ui_test_wrong_payment_mode_outgoing_payment",
    title="Wrong Payment Mode outgoing payment",
    source_section_value=organisation,
    destination_section_value=organisation,
    source_payment_value=bank_account,
    start_date=DateTime('2019/10/22'),
    resource_value=portal.currency_module.euro,
    payment_mode_value=portal.portal_categories.payment_mode.check,
    specialise_value=portal.business_process_module.erp5_default_business_process,
)
wrong_payment_mode_outgoing_payment.bank.edit(
    source_value=portal.account_module.bank,
    source_credit=100,
)
wrong_payment_mode_outgoing_payment.stop()

wrong_currency_outgoing_payment = portal.accounting_module.newContent(
    portal_type='Payment Transaction',
    id="erp5_payment_mean_ui_test_wrong_currency_outgoing_payment",
    title="Wrong Currency outgoing payment",
    source_section_value=organisation,
    destination_section_value=organisation,
    source_payment_value=bank_account,
    start_date=DateTime('2019/10/23'),
    resource_value=portal.currency_module.yen,
    payment_mode_value=portal.portal_categories.payment_mode.cash,
    specialise_value=portal.business_process_module.erp5_default_business_process,
)
wrong_currency_outgoing_payment.bank.edit(
    source_value=portal.account_module.bank,
    source_credit=100,
)
wrong_currency_outgoing_payment.stop()

return "Test Data Created."
