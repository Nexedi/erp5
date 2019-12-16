"""Create data set for aged balance:
$last_month: Purchase invoice 1 (500)
$last_month: Sale invoice 2 (300)
$next_month: Payment 1 (500)
$this_month + one_day: Payment 2 (300)
"""
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery
from DateTime import DateTime

portal = context.getPortalObject()
account_module = portal.account_module
organisation_module = portal.organisation_module

now = DateTime()
this_month = DateTime(now.year(), now.month(), 1)
last_month = this_month - 1
next_month = this_month + 32
later_this_month = this_month + 8

def get_object_by_title(portal_type, title):
  """Use portal catalog to search&fetch the object."""
  result = portal.portal_catalog(
    portal_type=portal_type,
    title=SimpleQuery(title=title, comparison_operator='='))
  if len(result) == 1:
    return result[0].getObject()
  return None


bank1 = get_object_by_title(portal_type='Bank Account', title='Bank1')
if bank1 is None:
  bank1 = portal.AccountingModule_createAccountingTestDocument(
    portal_type='Bank Account', title='Bank1', simulation_state='validated', 
    parent=organisation_module.my_organisation)

purchase1 = portal.AccountingModule_createAccountingTestDocument(
    portal_type='Purchase Invoice Transaction',
    title='Purchase invoice 1',
    destination_reference='1',
    source_reference='no',
    reference='ref1',
    simulation_state='delivered',
    ledger='',
    source_section_value=organisation_module.supplier,
    start_date=last_month,
    embedded=(dict(portal_type='Purchase Invoice Transaction Line',
              destination_value=account_module.goods_purchase,
              destination_debit=500.0),
              dict(portal_type='Purchase Invoice Transaction Line',
              destination_value=account_module.payable,
              destination_credit=500.0)),
    )

sale2 = portal.AccountingModule_createAccountingTestDocument(
    portal_type='Sale Invoice Transaction',
    title='Sale invoice 2',
    source_reference='2',
    destination_reference='no',
    reference='ref2',
    simulation_state='delivered',
    ledger='',
    destination_section_value=organisation_module.client_1,
    start_date=last_month,
    embedded=(dict(portal_type='Sale Invoice Transaction Line',
              source_value=account_module.goods_sales,
              source_credit=300.0),
              dict(portal_type='Sale Invoice Transaction Line',
              source_value=account_module.receivable,
              source_debit=300.0)),
    )

portal.Zuite_waitForActivities()

payment3 = portal.AccountingModule_createAccountingTestDocument(
    portal_type='Payment Transaction',
    title='Payment 1',
    source_reference='3',
    destination_reference='no',
    simulation_state='delivered',
    ledger='',
    causality_value=purchase1,
    payment_mode='payment_mode',
    destination_section_value=organisation_module.supplier,
    start_date=next_month,
    embedded=(dict(portal_type='Accounting Transaction Line',
              source_value=account_module.payable,
              source_debit=500.0),
              dict(portal_type='Accounting Transaction Line',
              source_value=account_module.bank,
              source_credit=500.0)),
    )

payment4 = portal.AccountingModule_createAccountingTestDocument(
    portal_type='Payment Transaction',
    title='Payment 2',
    source_reference='4',
    destination_reference='4',
    simulation_state='delivered',
    causality_value=sale2,
    payment_mode='payment_mode',
    ledger='',
    destination_section_value=organisation_module.client_1,
    start_date=later_this_month,
    embedded=(dict(portal_type='Accounting Transaction Line',
              source_value=account_module.bank,
              source_debit=300.0),
              dict(portal_type='Accounting Transaction Line',
              source_value=account_module.receivable,
              source_credit=300.0)),
    )

# we should have all receivable and payable lines grouped.
for transaction in [purchase1, sale2, payment3, payment4]:
  for line in transaction.getMovementList():
    if (line.getSourceValue() in (account_module.receivable,
                                  account_module.payable) or
        line.getDestinationValue() in (account_module.receivable,
                                       account_module.payable)):
      assert line.getGroupingReference()
      assert line.getGroupingDate()
