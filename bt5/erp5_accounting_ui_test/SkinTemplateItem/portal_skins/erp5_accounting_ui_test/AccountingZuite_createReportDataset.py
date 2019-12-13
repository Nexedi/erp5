"""Create Dataset for basic Trial Balance Report such as defined at
https://lab.nexedi.com/nexedi/erp5/blob/master/product/ERP5/tests/testAccountingReports.py#L563

The test operates on 'today' transactions.
"""

from DateTime import DateTime

portal = context.getPortalObject()
person_module = portal.person_module
account_module = portal.account_module
organisation_module = portal.organisation_module

one_hour = 1.0 / 24.0
one_day = 1.0
now = DateTime()
today = DateTime(now.year(), now.month(), now.day()) + 8 * one_hour
yesterday = today - one_day
tomorrow = today + one_day

bank1 = context.AccountingZuite_createDocument(
  parent=organisation_module.my_organisation,
  portal_type='Bank Account',
  title='Bank1',
  simulation_state='validated'
)
bank2 = bank1

if two_banks:
  bank2 = context.AccountingZuite_createDocument(
    parent=organisation_module.my_organisation,
    portal_type='Bank Account',
    title='Bank2',
    simulation_state='validated'
  )


context.AccountingZuite_createDocument(
  portal_type='Accounting Transaction',
  title='Transaction 1',
  source_reference='1',
  reference='ref1',
  simulation_state='delivered',
  destination_section_value=organisation_module.client_1,
  start_date=yesterday,
  embedded=(dict(portal_type='Accounting Transaction Line',
            source_value=account_module.receivable,
            source_debit=100.0),
            dict(portal_type='Accounting Transaction Line',
            source_value=account_module.payable,
            source_credit=100.0)),
  )

context.AccountingZuite_createDocument(
  portal_type='Accounting Transaction',
  title='Transaction 2',
  source_reference='2',
  reference='ref2',
  simulation_state='delivered',
  destination_section_value=organisation_module.client_1,
  start_date=yesterday + one_hour,
  embedded=(dict(portal_type='Accounting Transaction Line',
            source_value=account_module.payable,
            source_debit=200.0),
            dict(portal_type='Accounting Transaction Line',
            source_value=account_module.receivable,
            source_credit=200.0)),
  )

# in the period

context.AccountingZuite_createDocument(
  portal_type='Payment Transaction',
  title='Transaction 3',
  source_reference='3',
  reference='ref3',
  simulation_state='delivered',
  source_payment_value=bank1,
  destination_section_value=organisation_module.client_1,
  start_date=today + one_hour,
  embedded=(dict(portal_type='Accounting Transaction Line',
            source_value=account_module.receivable,
            source_debit=300.0),
            dict(portal_type='Accounting Transaction Line',
            source_value=account_module.bank,
            source_credit=300.0)),
  )

context.AccountingZuite_createDocument(
  portal_type='Payment Transaction',
  title='Transaction 4',
  destination_reference='4',
  reference='ref4',
  simulation_state='delivered',
  destination_section_value=organisation_module.my_organisation,
  destination_payment_value=bank1,
  source_section_value=organisation_module.client_2,
  stop_date=today + 2 * one_hour,
  start_date=yesterday,
  embedded=(dict(portal_type='Accounting Transaction Line',
            destination_value=account_module.receivable,
            destination_debit=400.0),
            dict(portal_type='Accounting Transaction Line',
            destination_value=account_module.bank,
            destination_credit=400.0)),
  )

context.AccountingZuite_createDocument(
  portal_type='Accounting Transaction',
  title='Transaction 5',
  source_reference='5',
  reference='ref5',
  simulation_state='delivered',
  source_payment_value=bank2,
  destination_section_value=person_module.john_smith,
  start_date=today + 3 * one_hour,
  embedded=(dict(portal_type='Accounting Transaction Line',
            source_value=account_module.receivable,
            source_debit=500.0),
            dict(portal_type='Accounting Transaction Line',
            source_value=account_module.bank,
            source_credit=500.0)),
  )

context.AccountingZuite_createDocument(
  portal_type='Purchase Invoice Transaction',
  title='Transaction 6',
  destination_reference='6',
  reference='ref6',
  simulation_state='delivered',
  destination_payment_value=bank2,
  source_section_value=organisation_module.client_1,
  start_date=yesterday + 2 * one_hour,
  stop_date=today + 4 * one_hour,
  embedded=(dict(portal_type='Purchase Invoice Transaction Line',
            destination_value=account_module.receivable,
            destination_debit=600.0),
            dict(portal_type='Purchase Invoice Transaction Line',
            destination_value=account_module.bank,
            destination_credit=600.0)),
  )

# another simulation state

context.AccountingZuite_createDocument(
  portal_type='Accounting Transaction',
  title='Transaction 7',
  source_reference='7',
  reference='ref7',
  simulation_state='stopped',
  source_payment_value=bank2,
  destination_section_value=organisation_module.client_1,
  start_date=today + 5 * one_hour,
  embedded=(dict(portal_type='Accounting Transaction Line',
            source_value=account_module.receivable,
            source_debit=700.0),
            dict(portal_type='Accounting Transaction Line',
            source_value=account_module.bank,
            source_credit=700.0)),
  )

# after the period

context.AccountingZuite_createDocument(
  portal_type='Accounting Transaction',
  title='Transaction 8',
  source_reference='8',
  reference='ref8',
  simulation_state='delivered',
  source_payment_value=bank2,
  destination_section_value=organisation_module.client_1,
  start_date=tomorrow,
  embedded=(dict(portal_type='Accounting Transaction Line',
            source_value=account_module.receivable,
            source_debit=800.0),
            dict(portal_type='Accounting Transaction Line',
            source_value=account_module.bank,
            source_credit=800.0)),
  )
