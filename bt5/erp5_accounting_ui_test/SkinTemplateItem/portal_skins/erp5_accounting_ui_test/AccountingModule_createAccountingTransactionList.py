from DateTime import DateTime
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery

# params
section_title = 'My Organisation'
portal = context.getPortalObject()
accounting_module = portal.accounting_module
year = 2005
default_date = DateTime(year, 01, 01)

business_process = portal.portal_catalog.getResultValue(
  reference=('default_erp5_business_process', # erp5_configurator
             'erp5_default_business_process'), # erp5_simulation_test
  portal_type='Business Process').getRelativeUrl()

# if the previous test didn't change input data, no need to recreate content
current_script_data_id = '%s_month_count_%s_draft_%s_state_%s_payment_%s_leger_%s' % (
     month_count, add_draft_transactions, transaction_state,
     add_related_payments, set_ledger, script.getId())

if accounting_module.getProperty('current_content_script',
                                '') == current_script_data_id:
  return "Accounting Transactions Created."

# first, cleanup accounting module
# XXX should be done in an external script / tool, because we have to
# workaround some security checks
if 1:
  for module_id in ['accounting_module',
                    'sale_packing_list_module',
                    'portal_simulation', ]:
    module = portal[module_id]
    if len(module) > 200:
      raise ValueError("Do not run this on production !!!")
    module.manage_delObjects(list(module.objectIds()))

# if `set_ledger`is true, allow all test ledgers in accounting types.
for accounting_type_id in portal.getPortalAccountingTransactionTypeList():
  accounting_type = portal.portal_types[accounting_type_id]
  accounting_type.edit(
    ledger_value_list=list(portal.portal_categories.ledger.test_accounting.contentValues())
    if set_ledger else ())

test_ledger_1 = None
if set_ledger:
  test_ledger_1 = portal.portal_categories.ledger.test_accounting.test_ledger_1

def getAccountByTitle(title):
  account_list = [x.getObject().getRelativeUrl() for x in
    portal.portal_catalog(portal_type='Account',
                          title=SimpleQuery(title=title, comparison_operator='='))]
  assert len(account_list) == 1, \
        '%d account with title "%s"' % (len(account_list), title)
  return account_list[0]

def getOrganisationByTitle(title):
  document_list = [x.getObject().getRelativeUrl() for x in
    portal.portal_catalog(portal_type='Organisation',
                          title=SimpleQuery(title=title, comparison_operator='='))]
  assert len(document_list) == 1, \
        '%d organisation with title "%s"' % (len(document_list), title)
  return document_list[0]
section = getOrganisationByTitle(section_title)

euro_resource = 'currency_module/euro'


product_list = [o.getObject() for o in portal.portal_catalog(
                                  portal_type='Product',
                                  title=SimpleQuery(title='Dummy Product for testing', comparison_operator='='))]
if product_list:
  product = product_list[0]
else:
  product = portal.product_module.newContent(portal_type='Product',
                              title='Dummy Product for testing')

for _ in range(random.randint(5, 10)):
  pl = portal.sale_packing_list_module.newContent(
        portal_type='Sale Packing List',
        title='Dummy Packing List for testing',
        source_section=section,
        source=section,
        destination_section=getOrganisationByTitle('Client 1'),
        destination=getOrganisationByTitle('Client 1'),
        specialise=business_process,
        start_date=default_date, )
  line = pl.newContent(portal_type='Sale Packing List Line',
                resource_value=product,
                quantity=random.randint(300, 500),
                price=random.randint(300, 500))

  # TODO: add an external method to modify workflow state of an object
  #context.portal_tests.setSimulationStateFor(pl, 'stopped')
  #assert pl.getSimulationState() == 'stopped'
  #pl.recursiveReindexObject()

for month in range(1, month_count + 1):
  default_date = DateTime(year, month, 1)
  tr = accounting_module.newContent(
        title='Accounts opening',
        portal_type='Accounting Transaction',
        source_section=section,
        created_by_builder=1,
        ledger_value=test_ledger_1,
        start_date=default_date,
        stop_date=default_date,
        resource=euro_resource,
    )

  tr.newContent(portal_type='Accounting Transaction Line',
                source=getAccountByTitle('Equity'),
                quantity=20000)
  tr.newContent(portal_type='Accounting Transaction Line',
                source=getAccountByTitle('Fixed Assets'),
                quantity=-15000)
  tr.newContent(portal_type='Accounting Transaction Line',
                source=getAccountByTitle('Stocks'),
                quantity=-5000)
  # TODO: "validated" should be renamed to "stopped"
  if transaction_state == 'validated':
    tr.stop()
    assert tr.getSimulationState() == 'stopped'
  elif transaction_state == 'delivered':
    tr.stop()
    tr.deliver()
    assert tr.getSimulationState() == 'delivered'
  else:
    # other cases not supported for now
    assert transaction_state == 'draft'

  vat_rate = .1

  for client_title, amount  in (('Client 1', 2000), ('Client 2', 3000)):
    default_date += 1
    tr = accounting_module.newContent(
          portal_type='Sale Invoice Transaction',
          title='%s Sale Invoice' % client_title,
          source_section=section,
          destination_section=getOrganisationByTitle(client_title),
          source=section,
          destination=getOrganisationByTitle(client_title),
          created_by_builder=1,
          ledger_value=test_ledger_1,
          start_date=default_date,
          stop_date=default_date,
          specialise=business_process,
          resource=euro_resource,
      )
    tr.newContent(portal_type='Sale Invoice Transaction Line',
                  source=getAccountByTitle('Receivable'),
                  quantity=-(amount * (1 + vat_rate)))
    tr.newContent(portal_type='Sale Invoice Transaction Line',
                  source=getAccountByTitle('Collected VAT 10%'),
                  quantity=amount * vat_rate)
    tr.newContent(portal_type='Sale Invoice Transaction Line',
                  source=getAccountByTitle('Goods Sales'),
                  quantity=amount)
    # add a random invoice line, which should not impact our tests
    tr.newContent(portal_type='Invoice Line',
                  source=section,
                  destination=getOrganisationByTitle(client_title),
                  resource_value=product,
                  quantity=random.randint(300, 400),
                  price=random.randint(300, 400), )
    if transaction_state == 'validated':
      tr.stop()
      assert tr.getSimulationState() == 'stopped'
    elif transaction_state == 'delivered':
      tr.stop()
      tr.deliver()
      assert tr.getSimulationState() == 'delivered'
    else:
      # other cases not supported for now
      assert transaction_state == 'draft'
    if add_related_payments:
      payment = accounting_module.newContent(
            causality_value=tr,
            portal_type='Payment Transaction',
            title='%s Payment' % client_title,
            source_section=section,
            destination_section=getOrganisationByTitle(client_title),
            created_by_builder=1,
            ledger_value=test_ledger_1,
            start_date=default_date + .1, # make sure this will be after the invoice
            stop_date=default_date + .1,
            resource=euro_resource,
        )
      payment.newContent(portal_type='Accounting Transaction Line',
                    source=getAccountByTitle('Bank'),
                    quantity=-(amount * (1 + vat_rate)))
      payment.newContent(portal_type='Accounting Transaction Line',
                    source=getAccountByTitle('Receivable'),
                    quantity=(amount * (1 + vat_rate)))
      if transaction_state in ('validated', 'delivered'):
        payment.stop()
        assert payment.getSimulationState() == 'stopped'
        if transaction_state == 'delivered':
          tr.deliver()
          assert tr.getSimulationState() == 'delivered'
        if not keep_grouping_reference:
          tag = script.id + '_payment_indexation_' + payment.getPath()
          payment.recursiveReindexObject(activate_kw={'tag': tag})
          for line in payment.getMovementList(
                          portal_type=payment.getPortalAccountingMovementTypeList()):
            if line.getGroupingReference():
              line.activate(after_tag=tag).AccountingTransactionLine_resetGroupingReference()

      else:
        # other cases not supported for now
        assert transaction_state == 'draft'
      

  amount=7000
  default_date += 1
  tr = accounting_module.newContent(
        portal_type='Purchase Invoice Transaction',
        title='First Purchase Invoice',
        destination_section=section,
        source_section=getOrganisationByTitle('Supplier'),
        created_by_builder=1,
        ledger_value=test_ledger_1,
        start_date=default_date-5, # In purchase invoice transaction, stop_date is accounting operation date.
        stop_date=default_date,
        specialise=business_process,
        resource=euro_resource,
    )
  tr.newContent(portal_type='Purchase Invoice Transaction Line',
                destination=getAccountByTitle('Payable'),
                quantity=-(amount * (1 + vat_rate)))
  tr.newContent(portal_type='Purchase Invoice Transaction Line',
                destination=getAccountByTitle('Refundable VAT 10%'),
                quantity=amount * vat_rate)
  tr.newContent(portal_type='Purchase Invoice Transaction Line',
                destination=getAccountByTitle('Goods Purchase'),
                quantity=amount)
  if transaction_state == 'validated':
    tr.stop()
    assert tr.getSimulationState() == 'stopped'
  elif transaction_state == 'delivered':
    tr.stop()
    tr.deliver()
    assert tr.getSimulationState() == 'delivered'
  else:
    # other cases not supported for now
    assert transaction_state == 'draft'
  
if add_draft_transactions:
  # finally, add random accounting transcactions in draft state, which have no
  # impact on the test
  for client_title, amount  in (('Client 1', 2000), ('Client 2', 3000)):
    tr = accounting_module.newContent(
          portal_type='Sale Invoice Transaction',
          title='%s Sale Invoice' % client_title,
          source_section=section,
          destination_section=getOrganisationByTitle(client_title),
          created_by_builder=1,
          ledger_value=test_ledger_1,
          start_date=default_date,
          stop_date=default_date,
          resource=euro_resource,
          specialise=business_process,
      )
    tr.newContent(portal_type='Sale Invoice Transaction Line',
                  source=getAccountByTitle('Receivable'),
                  quantity=random.randint(300, 400),)
    tr.newContent(portal_type='Sale Invoice Transaction Line',
                  source=getAccountByTitle('Collected VAT 10%'),
                  quantity=random.randint(300, 400),)
    tr.newContent(portal_type='Sale Invoice Transaction Line',
                  source=getAccountByTitle('Goods Sales'),
                  quantity=random.randint(300, 400),)

accounting_module.setProperty('current_content_script',
                              current_script_data_id)

# test depends on this
return "Accounting Transactions Created."
# vim: syntax=python
