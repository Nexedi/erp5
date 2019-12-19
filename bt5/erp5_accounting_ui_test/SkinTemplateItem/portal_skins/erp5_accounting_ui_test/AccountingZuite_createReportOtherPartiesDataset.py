"""Create Dataset for basic Trial Balance Report such as defined at
https://lab.nexedi.com/nexedi/erp5/blob/master/product/ERP5/tests/testAccountingReports.py#L4583

The test operates on 'today' transactions.

:param with_ledger: if true then data are prepared for 
    testOtherPartiesReportLedger unittest rather than testOtherPartiesReport
"""

from DateTime import DateTime

portal = context.getPortalObject()
accounting_module = portal.accounting_module
account_module = portal.account_module
ledger = portal.portal_categories.ledger
organisation_module = portal.organisation_module
person_module = portal.person_module

one_hour = 1.0 / 24.0
now = DateTime()
today = DateTime(now.year(), now.month(), now.day()) + 8 * one_hour

if with_ledger:
    extra_kwargs_general = {'ledger': 'accounting/general'}
    extra_kwargs_detailed = {'ledger': 'accounting/detailed'}

    accounting_ledger = ledger.get('accounting', None)
    if accounting_ledger is None:
        accounting_ledger = ledger.newContent(portal_type='Category', id='accounting')

    for sub_category_name in ('general', 'detailed'):
        sub_category = accounting_ledger.get(sub_category_name, None)
        if sub_category is None:
            sub_category = accounting_ledger.newContent(portal_type='Category', id=sub_category_name)

    # necessary for the "ledger" form field to appear and have correct options
    accounting_transaction = portal.portal_types.get('Accounting Transaction')
    ledger_list = accounting_transaction.getLedgerList()
    if 'accounting/general' not in ledger_list:
        ledger_list.append('accounting/general')
    if 'accounting/detailed' not in ledger_list:
        ledger_list.append('accounting/detailed')
    accounting_transaction.setLedgerList(ledger_list)

else:
    extra_kwargs_general = {}
    extra_kwargs_detailed = {}

context.AccountingTransactionModule_createAccountingTestDocument(
    portal_type='Accounting Transaction',
    title='Transaction 1',
    source_reference='1',
    simulation_state='delivered',
    destination_section_value=organisation_module.client_1,
    start_date=today + 1 * one_hour,
    embedded=(dict(portal_type='Accounting Transaction Line',
              source_value=account_module.receivable,
              source_debit=100.0),
              dict(portal_type='Accounting Transaction Line',
              source_value=account_module.goods_sales,
              source_credit=100.0)),
    **extra_kwargs_general
    )

context.AccountingTransactionModule_createAccountingTestDocument(
    portal_type='Accounting Transaction',
    title='Transaction 2',
    source_reference='2',
    simulation_state='delivered',
    destination_section_value=organisation_module.client_1,
    start_date=today + 2 * one_hour,
    embedded=(dict(portal_type='Accounting Transaction Line',
              source_value=account_module.payable, source_debit=200.0),
              dict(portal_type='Accounting Transaction Line',
              source_value=account_module.goods_sales,
              source_credit=200.0)),
    **extra_kwargs_general
    )

if with_ledger:
    context.AccountingTransactionModule_createAccountingTestDocument(
        portal_type='Accounting Transaction',
        title='Transaction 3',
        source_reference='3',
        simulation_state='delivered',
        destination_section_value=organisation_module.client_1,
        start_date=today + 3 * one_hour,
        embedded=(dict(portal_type='Accounting Transaction Line',
                  source_value=account_module.payable, source_debit=400.0),
                  dict(portal_type='Accounting Transaction Line',
                  source_value=account_module.goods_sales,
                  source_credit=400.0)),
        **extra_kwargs_detailed
        )
