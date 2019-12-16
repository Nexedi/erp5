from DateTime import DateTime

portal = context.getPortalObject()
accounting_module = portal.accounting_module
account_module = portal.account_module

one_hour = 1.0 / 24.0
today = DateTime(DateTime().Date()) + 8 * one_hour
yesterday = today - 1
tomorrow = today + 1


context.AccountingModule_createAccountingTestDocument(
  portal_type='Accounting Transaction',
  simulation_state='delivered',
  start_date=yesterday,
  embedded=[
    {"portal_type": 'Accounting Transaction Line',
     "source_value": account_module.equity,
     "source_debit": 100},
    {"portal_type": 'Accounting Transaction Line',
     "source_value": account_module.stocks,
     "source_credit": 100}
  ]
)
context.AccountingModule_createAccountingTestDocument(
  portal_type='Sale Invoice Transaction',
  title='First One',
  simulation_state='delivered',
  reference='1',
  destination_section_value=portal.organisation_module.client_1,
  start_date=today,
  embedded=[
    {"portal_type": 'Sale Invoice Transaction Line',
     "source_value": account_module.receivable,
     "source_debit": 119.60},
    {"portal_type": 'Sale Invoice Transaction Line',
     "source_value": account_module.collected_vat,
     "source_credit": 19.60},
    {"portal_type": 'Sale Invoice Transaction Line',
     "source_value": account_module.goods_sales,
     "source_credit": 100.00},
  ]
)
context.AccountingModule_createAccountingTestDocument(
  portal_type='Sale Invoice Transaction',
  title='Second One',
  simulation_state='delivered',
  reference='2',
  destination_section_value=portal.organisation_module.client_2,
  start_date=today + one_hour,
  # different values of hour minutes, because /for now/ sorting is
  # done on date, uid. Sorting on [source|destination]_reference
  # would be too heavy, and we just want a sort on date, with a
  # stable order (hence the cheap sort on uid)
  embedded=[
    {"portal_type": 'Sale Invoice Transaction Line',
     "source_value": account_module.receivable,
     "source_debit": 239.20},
    {"portal_type": 'Sale Invoice Transaction Line',
     "source_value": account_module.collected_vat,
     "source_credit": 39.20},
    {"portal_type": 'Sale Invoice Transaction Line',
     "source_value": account_module.goods_sales,
     "source_credit": 200.00},
  ]
)
context.AccountingModule_createAccountingTestDocument(
  portal_type='Sale Invoice Transaction',
  title='Third One',
  simulation_state='delivered',
  reference='3',
  destination_section_value=portal.person_module.john_smith,
  start_date=today + 2 * one_hour,
  embedded=[
    {"portal_type": 'Sale Invoice Transaction Line',
     "source_value": account_module.receivable,
     "source_debit": 358.80},
    {"portal_type": 'Sale Invoice Transaction Line',
     "source_value": account_module.collected_vat,
     "source_credit": 58.80},
    {"portal_type": 'Sale Invoice Transaction Line',
     "source_value": account_module.goods_sales,
     "title": 'Line Title',
     "source_credit": 300.00},
  ]
)
context.AccountingModule_createAccountingTestDocument(
  portal_type='Accounting Transaction',
  simulation_state='delivered',
  start_date=today,
  embedded=[
    {"portal_type": 'Accounting Transaction Line',
     "source_value": account_module.equity,
     "source_debit": 111},
    {"portal_type": 'Accounting Transaction Line',
     "source_value": account_module.stocks,
     "source_credit": 111},
  ]
)
context.AccountingModule_createAccountingTestDocument(
  portal_type='Sale Invoice Transaction',
  simulation_state='delivered',
  destination_section_value=portal.organisation_module.client_2,
  start_date=tomorrow,
  embedded=[
    {"portal_type": "Sale Invoice Transaction Line",
     "source_value": account_module.receivable,
     "source_debit": 598.00},
    {"portal_type": "Sale Invoice Transaction Line",
     "source_value": account_module.collected_vat,
     "source_credit": 98.00},
    {"portal_type": "Sale Invoice Transaction Line",
     "source_value": account_module.goods_sales,
     "source_credit": 500.00}])
