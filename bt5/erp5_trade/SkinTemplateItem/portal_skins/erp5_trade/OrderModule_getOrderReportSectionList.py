from Products.ERP5Form.Report import ReportSection
from Products.ERP5Type.DateUtils import getIntervalListBetweenDates
from DateTime import DateTime
result=[]

request = container.REQUEST
# list only if user has a login defined
aggregation_level = request.get('aggregation_level')
from_date = request.get('from_date')
to_date = request.get('at_date')
group_by = request.get('group_by')
quantity_unit = request.get('quantity_unit')
simulation_state = request.get('simulation_state', ())

# define some parameter dependings on module
if "Sale" in context.getPortalType():
  report_type = "sale"
  if 'Sale Order' in context.getPortalType():
    doc_portal_type = "Sale Order"
    line_portal_type = "Sale Order Line"
  else:
    line_portal_type = "Sale Packing List Line"
    doc_portal_type = "Sale Packing List"
elif "Purchase" in context.getPortalType():
  report_type = "purchase"
  line_portal_type = "Purchase Order Line"
  doc_portal_type = "Purchase Order"
elif request.get('order_report_document_portal_type'):
  doc_portal_type = request.get('order_report_document_portal_type')
  if doc_portal_type == 'Purchase Invoice Transaction':
    line_portal_type = 'Invoice Line'
    report_type = 'purchase'
  elif doc_portal_type == 'Sale Invoice Transaction':
    line_portal_type = 'Invoice Line'
    report_type = 'sale'
  else:
    raise ValueError, "unknown document portal type for report %s" % doc_portal_type
else:
  raise ValueError, "unknown type for report"

selection_columns = [('group_by', "Group by")]
if from_date is None:
  # get the minimum start date in catalog
  from Products.ZSQLCatalog.SQLCatalog import Query, NegatedQuery
  kw = {"delivery.start_date" : None, "key":"DefaultKey"}
  q = NegatedQuery(Query(**kw))
  from_date = DateTime()
  result_list = context.portal_catalog(
    sort_on=(('delivery.start_date','ascending'),),
    portal_type=doc_portal_type,
    query=q,
    limit=1)
  if result_list:
    from_date = result_list[0].getStartDate()

# get period list between given date
interval_list_dict = getIntervalListBetweenDates(from_date=from_date, to_date=to_date,
                                            keys={'year':aggregation_level=="year",
                                                  'month':aggregation_level=="month",
                                                  'week' : aggregation_level=="week",
                                                  'day':aggregation_level=="day"})
interval_list = interval_list_dict[aggregation_level]

# FIXME: translate column names
# list columns of the listbox
interval_column_list = []
if group_by == "client":
  interval_column_list.extend([("Amount %s" %x,"Amount %s" %x) for x in interval_list])
  selection_columns = [('client', "Client")]
  stat_columns = [('client', "client")]
  total_column_list = [('total amount', 'Total Amount'),]
  total_stat_list = [('total amount', 'total amount'),]
else:
  if group_by == "product":
    selection_columns = [('product_reference', "Product Reference", ), ('product', "Product"), ('ean13_code', 'Ean13 code')]
    stat_columns = [('product', "product")]
  elif group_by == "function":
    function_title = context.AccountingTransactionLine_getFunctionBaseCategoryTitle()
    selection_columns = [('product', function_title)]
    stat_columns = [('product', "product")]
  else:
    selection_columns = [('client', "Client"), ('product_reference', "Product Reference", ), ('product', "Product"), ('ean13_code', 'Ean13 code')]
    stat_columns = [('client', "client"), ('product', "product")]
  for x in interval_list:
    interval_column_list.extend([("Amount %s" %x,"Amount %s" %x), ("Quantity %s" %x,"Quantity %s" %x)])
    if not quantity_unit:
      interval_column_list.extend([("Quantity Unit %s" %x,"Quantity Unit %s" %x)])
  total_column_list = [('total amount', 'Total Amount'),('total quantity', 'Total Quantity')]
  total_stat_list = [('total amount', 'total amount'),('total quantity', 'total quantity')]

selection_columns.extend(interval_column_list)
selection_columns.extend(total_column_list)

params=dict(period_list=interval_list, report_type=report_type,
            doc_portal_type=doc_portal_type, line_portal_type=line_portal_type,
            simulation_state=simulation_state)

# stat columns of the listbox
stat_columns = stat_columns + interval_column_list + total_stat_list
context.REQUEST.set('stat_columns', stat_columns)

result.append(ReportSection(
              path=context.getPhysicalPath(),
              selection_columns=selection_columns,
              listbox_display_mode='FlatListMode',
              selection_params=params,
              form_id='OrderModule_viewOrderStatList'))


return result
