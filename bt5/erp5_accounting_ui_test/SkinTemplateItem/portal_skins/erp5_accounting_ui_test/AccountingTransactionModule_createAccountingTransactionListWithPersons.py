# params
section_title = 'My Organisation'
business_process = 'business_process_module/erp5_default_business_process'
portal = context.getPortalObject()
accounting_module = portal.accounting_module
from DateTime import DateTime
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery
year = 2005

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
  for module_id in ['accounting_module',
                    'sale_packing_list_module',
                    'portal_simulation', ]:
    module = portal[module_id]
    module.manage_delObjects(list(module.objectIds()))

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

def getPersonByTitle(title):
  document_list = [x.getObject().getRelativeUrl() for x in
    portal.portal_catalog(portal_type='Person',
                          title=SimpleQuery(title=title, comparison_operator='='))]
  assert len(document_list) == 1, \
        '%d person with title "%s"' % (len(document_list), title)
  return document_list[0]

def getCurrencyByReference(reference):
  document_list = [x.getObject().getRelativeUrl() for x in
    portal.portal_catalog(portal_type='Currency',
                          reference=reference)]
  assert len(document_list) == 1, \
      '%d currency with reference "%s"' % (len(document_list), reference)
  return document_list[0]
euro_resource = getCurrencyByReference('EUR')

for month in range(1, month_count + 1):
  day = 1
  vat_rate = .1
  for client_title, amount  in (('John Smith', 1000),):
    tr = accounting_module.newContent(
          portal_type='Sale Invoice Transaction',
          title='%s Sale Invoice' % client_title,
          source_section=section,
          destination_section=getPersonByTitle(client_title),
          created_by_builder=1,
          start_date=DateTime(year, month, day),
          stop_date=DateTime(year, month, day),
          specialise=business_process,
          resource=euro_resource,
      )
    tr.newContent(portal_type='Sale Invoice Transaction Line',
                  source=getAccountByTitle('Receivable'),
                  destination=getAccountByTitle('Payable'),
                  quantity=-(amount * (1 + vat_rate)))
    tr.newContent(portal_type='Sale Invoice Transaction Line',
                  source=getAccountByTitle('Collected VAT 10%'),
                  destination=getAccountByTitle('Refundable VAT 10%'),
                  quantity=amount * vat_rate)
    tr.newContent(portal_type='Sale Invoice Transaction Line',
                  source=getAccountByTitle('Goods Sales'),
                  destination=getAccountByTitle('Goods Purchase'),
                  quantity=amount)
    tr.stop()
    tr.setSourceReference('source_reference')
    tr.setDestinationReference('destination_reference')

accounting_module.setProperty('current_content_script',
                              current_script_data_id)

# test depends on this
return "Accounting Transactions Created."
# vim: syntax=python
