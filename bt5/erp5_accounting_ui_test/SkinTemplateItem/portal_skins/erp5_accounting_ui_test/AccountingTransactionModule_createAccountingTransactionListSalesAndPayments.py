from DateTime import DateTime
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery

# params
section_title = 'My Organisation'
business_process = 'business_process_module/erp5_default_business_process'
portal = context.getPortalObject()
accounting_module = portal.accounting_module
year = 2005

total_receivable_quantity = 0

# if the previous test didn't change input data, no need to recreate content
current_script_data_id = '%s_month_count_%s' % (
                                 month_count, script.getId())
if accounting_module.getProperty('current_content_script',
                                '') == current_script_data_id:
  return "Accounting Transactions Created."

# first, cleanup accounting module
# XXX should be done in an external script / tool, because we have to
# workaround some security checks
if 1:
  accounting_module.manage_delObjects(list(accounting_module.objectIds()))

# XXX copy & paste 
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

def getCurrencyByReference(reference):
  document_list = [x.getObject().getRelativeUrl() for x in
    portal.portal_catalog(portal_type='Currency',
                          reference=reference)]
  assert len(document_list) == 1, \
      '%d currency with reference "%s"' % (len(document_list), reference)
  return document_list[0]
euro_resource = getCurrencyByReference('EUR')

def getBankAccountByTitle(title):
  document_list = [x.getObject().getRelativeUrl() for x in
    portal.portal_catalog(portal_type='Bank Account',
                          title=SimpleQuery(title=title, comparison_operator='='))]
  assert len(document_list) == 1, \
      '%d Bank Account with title "%s"' % (len(document_list), title)
  return document_list[0]

for month in range(1, month_count + 1):
  for day in range(1, 29):
    vat_rate = .1
    for client_title, amount  in (('Client 1', 1000 * day),
                                  ('Client 2', 2000 * day) ):
      tr = accounting_module.newContent(
            portal_type='Sale Invoice Transaction',
            title='%s Sale Invoice' % client_title,
            source_section=section,
            destination_section=getOrganisationByTitle(client_title),
            created_by_builder=1,
            start_date=DateTime(year, month, day),
            stop_date=DateTime(year, month, day),
            resource=euro_resource,
            specialise=business_process,
        )
      receivable_qty = -(amount * (1 + vat_rate))
      total_receivable_quantity += receivable_qty
      tr.newContent(portal_type='Sale Invoice Transaction Line',
                    source=getAccountByTitle('Receivable'),
                    destination=getAccountByTitle('Payable'),
                    quantity=receivable_qty,
      )
      tr.newContent(portal_type='Sale Invoice Transaction Line',
                    source=getAccountByTitle('Collected VAT 10%'),
                    destination=getAccountByTitle('Refundable VAT 10%'),
                    quantity=amount * vat_rate,
      )
      tr.newContent(portal_type='Sale Invoice Transaction Line',
                    source=getAccountByTitle('Goods Sales'),
                    destination=getAccountByTitle('Goods Purchase'),
                    quantity=amount,
      )
      tr.stop()

      # payment
      ptr = accounting_module.newContent(
            portal_type='Payment Transaction',
            title='Payment from %s Sale Invoice' % client_title,
            source_section=section,
            source_payment=getBankAccountByTitle('My default bank account'),
            destination_section=getOrganisationByTitle(client_title),
            created_by_builder=1,
            start_date=DateTime(year, month, day, 01, 01) + 10,
            stop_date=DateTime(year, month, day, 01, 01) + 10,
            causality_value=tr,
            resource=euro_resource,
        )

      ptr.newContent(portal_type='Accounting Transaction Line',
                    source=getAccountByTitle('Receivable'),
                    quantity=(amount * (1 + vat_rate)),
      )
      ptr.newContent(portal_type='Accounting Transaction Line',
                    source=getAccountByTitle('Bank'),
                    quantity= - (amount * (1 + vat_rate)),
      )
      ptr.stop()

      if not keep_grouping_reference:
        tag = script.id + '_payment_indexation_' + ptr.getPath()
        ptr.recursiveReindexObject(activate_kw={'tag': tag})
        for line in ptr.getMovementList(
                          portal_type=ptr.getPortalAccountingMovementTypeList()):
          if line.getGroupingReference():
             line.activate(after_tag=tag).AccountingTransactionLine_resetGroupingReference()


accounting_module.setProperty('current_content_script',
                              current_script_data_id)

# test depends on this
return "Accounting Transactions Created."
# vim: syntax=python
