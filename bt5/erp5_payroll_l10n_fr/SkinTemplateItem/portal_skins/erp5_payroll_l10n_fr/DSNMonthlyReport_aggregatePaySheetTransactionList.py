# Aggregate the Pay Sheet Transactions that will be declared in
# the current DSN Report.
# Pay Sheet Transactions are found by date and organisation
from Products.ERP5Type.DateUtils import getNumberOfDayInMonth
from Products.ZSQLCatalog.SQLCatalog import ComplexQuery, Query

portal = context.getPortalObject()

effective_date = context.getEffectiveDate(None)
organisation = context.getSourceSectionValue(None)

from_date = DateTime(effective_date.year(), effective_date.month(), 1)
to_date = DateTime(from_date.year(), from_date.month(), getNumberOfDayInMonth(from_date))

# work can't be done if no date or no organisation is defined
if effective_date is None or organisation is None:
  context.REQUEST.response.redirect("%s?portal_status_message=%s" % 
    (context.absolute_url(), "Both End of Pay Period and Main Entreprise should be defined"))


catalog_kw = {'query': ComplexQuery(Query(start_date=">=%s" % from_date.strftime("%Y/%m/%d")),
                                    Query(stop_date="<=%s" % to_date.strftime("%Y/%m/%d")),
                                    Query(destination_section_uid=Query(destination_section_uid=organisation.getUid())),
                                    operator="AND")}

paysheet_list = portal.accounting_module.searchFolder(portal_type="Pay Sheet Transaction", **catalog_kw)

for paysheet in paysheet_list:
  paysheet = paysheet.getObject()
  aggregate_list = paysheet.getAggregateList([])
  if context.getRelativeUrl() not in aggregate_list:
    aggregate_list.append(context.getRelativeUrl())
    paysheet.edit(aggregate_list=aggregate_list)

context.REQUEST.response.redirect("%s?portal_status_message=%s" % 
  (context.absolute_url(), "Pay Sheet Transactions have been aggregated, DSN Report can be generated now."))
