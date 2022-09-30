# Aggregate the Pay Sheet Transactions that will be declared in
# the current DSN Report.
# Pay Sheet Transactions are chosen by date and establishment
from Products.ZSQLCatalog.SQLCatalog import ComplexQuery, Query

portal = context.getPortalObject()

destination_trade = portal.restrictedTraverse(destination_trade_category)

catalog_kw = {'query': ComplexQuery(Query(start_date=">=%s" % from_date.strftime("%Y/%m/%d")),
                                    Query(stop_date="<=%s" % to_date.strftime("%Y/%m/%d")),
                                    Query(destination_trade_uid=Query(destination_trade_uid=destination_trade.getUid())),
                                    Query(simulation_state='!=cancelled'),
                                    Query(simulation_state='!=deleted'),
                                    Query(simulation_state='!=draft'),
                                    logical_operator="AND")}

paysheet_list = portal.accounting_module.searchFolder(portal_type="Pay Sheet Transaction", **catalog_kw)

for paysheet in paysheet_list:
  paysheet = paysheet.getObject()
  aggregate_list = paysheet.getAggregateList([])
  if context.getRelativeUrl() not in aggregate_list:
    aggregate_list.append(context.getRelativeUrl())
    paysheet.edit(aggregate_list=aggregate_list)

context.REQUEST.response.redirect("%s?portal_status_message=%s" %
  (context.absolute_url(), "Pay Sheet Transactions have been aggregated, DSN Report can be generated now."))
