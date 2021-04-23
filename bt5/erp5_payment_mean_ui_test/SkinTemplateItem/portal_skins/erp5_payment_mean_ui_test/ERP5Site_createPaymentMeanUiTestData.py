from DateTime import DateTime

portal = context.getPortalObject()

# validate rules ( see Products.ERP5Type.tests.ERP5TypeTestCase )
for rule in portal.portal_rules.contentValues():
  if rule.getValidationState() != 'validated':
    rule.validate()

# validate other documents used in this test
for document in (
    portal.account_module.equity,
    portal.account_module.bank,
    portal.currency_module.euro, ):
  if document.getValidationState() != 'validated':
    document.validate()

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

for id_, date, resource_value, payment_mode_value, quantity, state, consistent in (
    ('erp5_payment_mean_ui_test_incoming_payment', DateTime('2019/10/20'), portal.currency_module.euro, portal.portal_categories.payment_mode.cash, -100, 'stopped', True),
    ('erp5_payment_mean_ui_test_outgoing_payment', DateTime('2019/10/20'), portal.currency_module.euro, portal.portal_categories.payment_mode.cash, 100, 'stopped', True),
    ('erp5_payment_mean_ui_test_second_outgoing_payment', DateTime('2019/10/21'), portal.currency_module.euro, portal.portal_categories.payment_mode.cash, 100, 'stopped', True),
    ('erp5_payment_mean_ui_test_planned_outgoing_payment', DateTime('2019/10/20'), portal.currency_module.euro, portal.portal_categories.payment_mode.cash, 100, 'planned', True),
    ('erp5_payment_mean_ui_test_confirmed_outgoing_payment', DateTime('2019/10/20'), portal.currency_module.euro, portal.portal_categories.payment_mode.cash, 100, 'confirmed', True),
    ('erp5_payment_mean_ui_test_confirmed_not_consistent_outgoing_payment', DateTime('2019/10/20'), portal.currency_module.euro, portal.portal_categories.payment_mode.cash, 100, 'confirmed', False),
    ('erp5_payment_mean_ui_test_wrong_payment_mode_outgoing_payment', DateTime('2019/10/20'), portal.currency_module.euro, portal.portal_categories.payment_mode.check, 100, 'stopped', True),
    ('erp5_payment_mean_ui_test_wrong_currency_outgoing_payment', DateTime('2019/10/20'), portal.currency_module.yen, portal.portal_categories.payment_mode.cash, 100, 'stopped', True),
):
  payment = portal.accounting_module.newContent(
      portal_type='Payment Transaction',
      id=id_,
      source_section_value=organisation,
      source_payment_value=bank_account,
      start_date=date,
      resource_value=resource_value,
      payment_mode_value=payment_mode_value,
      specialise_value=portal.business_process_module.erp5_default_business_process,
  )
  payment.bank.edit(
      source_value=portal.account_module.bank,
      quantity=quantity
  )
  payment.receivable.edit(
      source_value=portal.account_module.equity if consistent else None,
      quantity=-quantity
  )
  if state == 'planned':
    payment.plan()
  elif state == 'confirmed':
    payment.confirm()
  elif state == 'stopped':
    payment.stop()
  else:
    raise ValueError("unknown state", state)
return "Test Data Created."
