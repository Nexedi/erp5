if clean:
  context.Zuite_tearDownSaleOrderTest()

portal = context.getPortalObject()
howto_dict = context.Zuite_getHowToInfo()
isTransitionPossible = portal.portal_workflow.isTransitionPossible

# validate rules
for account in context.account_module.objectValues():
  if isTransitionPossible(account, 'validate'):
    account.validate()

business_process = context.portal_catalog.getResultValue(portal_type='Business Process',
                                                         reference='erp5_default_business_process')

# validate default business process
if context.portal_templates.getInstalledBusinessTemplate("erp5_simulation_test") is not None:
  business_process.account_debit_path.setTestTalesExpression('python: True')
  business_process.account_debit_path.setSourceValue(context.account_module.goods_sales)
  business_process.account_credit_path.setTestTalesExpression('python: True')
  business_process.account_credit_path.setSourceValue(context.account_module.receivable)
  if isTransitionPossible(business_process, 'validate'):
    business_process.validate()
# check if there is already the euro curency on the instance
currency = context.portal_catalog.getResultValue(portal_type='Currency',
                                                 title=howto_dict['sale_howto_currency_title'])
if currency is None:
  currency = portal.currency_module.newContent(portal_type='Currency',
                                               title=howto_dict['sale_howto_currency_title'],
                                               reference=howto_dict['sale_howto_currency_tag'],
                                               id=howto_dict['sale_howto_currency_tag'],
                                               base_unit_quantity=0.01)

if isTransitionPossible(currency, 'validate'):
  currency.validate()


# add default sale order trade condition
sale_order_trade_condition = context.portal_catalog.getResultValue(portal_type='Sale Trade Condition',
                                                                  reference='STC-General')
if sale_order_trade_condition is None:
  sale_order_trade_condition = context.sale_trade_condition_module.newContent(
                                                 portal_type='Sale Trade Condition',
                                                 reference='STC-General',
                                                 title='General Sale Trade Condition',
                                                 price_currency=currency.getRelativeUrl())
  sale_order_trade_condition.setSpecialiseValue(business_process)

if isTransitionPossible(sale_order_trade_condition, 'validate'):
  sale_order_trade_condition.validate()


product = portal.product_module.newContent(portal_type='Product',
                                           title=howto_dict['sale_howto_product_title'])
product.setSupplyLinePriceCurrency(currency.getRelativeUrl())
product.setBasePrice(1.0)
product.setQuantityUnit('unit/piece')
product.setBaseContribution('base_amount/taxable')
product.validate()

my_organisation = portal.organisation_module.newContent(portal_type='Organisation',
                                                        title=howto_dict['sale_howto_organisation_title'],
                                                        corporate_name=howto_dict['sale_howto_organisation_title'])
my_organisation.setRole('supplier')
my_organisation.setGroup('my_group')
my_organisation.validate()

bank_account = my_organisation.newContent(portal_type="Bank Account",
                           title=howto_dict["sale_howto_bank_account_title"],
                           reference=howto_dict["sale_howto_bank_account_reference"],)

organisation = portal.organisation_module.newContent(portal_type='Organisation',
                                                     title=howto_dict['sale_howto_organisation2_title'],
                                                     corporate_name=howto_dict['sale_howto_organisation2_title'])
organisation.validate()

person = portal.person_module.newContent(portal_type='Person',
                                         title=howto_dict['sale_howto_person_title'],
                                         career_subordination_title=howto_dict['sale_howto_organisation_title'])
person.validate()

pref = getattr(context.portal_preferences, howto_dict['howto_preference_id'], None)
if pref is None:
  pref = context.portal_preferences.newContent(portal_type="Preference",
                                               id=howto_dict['howto_preference_id'])
  pref.setPreferredAccountingTransactionSectionCategory('group/my_group')
if isTransitionPossible(pref, 'enable'):
  pref.enable()

pref.setPreferredAccountingTransactionSourceSection(my_organisation.getRelativeUrl())

# Disabling save form warning
# this is bad but needed quickly to disable save form warning
pref.setPreferredHtmlStyleUnsavedFormWarning(False)

my_organisation.activate(
  after_path_and_method_id=(
    my_organisation.getPath(), ('immediateRecusriveReindexObject', 'immediateReindexObject'))) \
  .Organisation_addConditionallyAccountingPeriod()

for rule_reference in ('default_delivering_rule',
                       'default_delivery_rule',
                       'default_accounting_transaction_rule',
                       'default_trade_model_rule',
                       'default_payment_rule',
                       'default_order_rule',
                       'default_invoice_transaction_rule',
                       'default_invoicing_rule',
                       'default_invoice_rule',):
  rule = portal.portal_rules.searchFolder(reference=rule_reference,
                                        sort_on='version',
                                        sort_order='descending')[0].getObject()
  if isTransitionPossible(rule, 'validate'):
    rule.validate()

# Clear cache
portal.portal_caches.clearAllCache()

return "Init Ok"
