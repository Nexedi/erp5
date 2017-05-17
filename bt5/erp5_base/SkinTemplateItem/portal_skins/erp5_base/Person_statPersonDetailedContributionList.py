request = container.REQUEST
RESPONSE =  request.RESPONSE

stat_line = request.get('stat_line', None)

return stat_line


# XXX example of another way to get the stat line but this is slower
from Products.ERP5Type.Log import log
from Products.PythonScripts.standard import Object
from Products.ZSQLCatalog.SQLCatalog import Query
request = container.REQUEST
from_date = request.get('from_date', None)
to_date = request.get('at_date', None)
aggregation_level = request.get('aggregation_level', None)
log("in stat method", "")
# build document portal type list
portal_type_list = []
extend = portal_type_list.extend
for title, path in context.ERP5Site_getModuleItemList():
  document_type_list = context.restrictedTraverse(path).allowedContentTypes()
  extend([x.id for x in document_type_list])

# compute sql params, we group and order by date and portal type
if aggregation_level == "year":
  sql_format = "%Y"
elif aggregation_level == "month":
  sql_format = "%Y-%m"
elif aggregation_level == "week":
  sql_format = "%Y-%u"
elif aggregation_level == "day":
  sql_format = "%Y-%m-%d"
count_kw = {}
if from_date is not None and to_date is not None:  
  count_kw['creation_date'] = {
    'range': 'minngt',
    'query': (from_date, to_date),
  }
elif from_date is not None:
  count_kw['creation_date'] = {
    'range': 'min',
    'query': from_date,
  }
elif to_date is not None:
  count_kw['creation_date'] = {
    'range': 'ngt',
    'query': to_date,
  }

# count number of object created by the user for each type of document
result_list = context.portal_catalog.countResults(select_dict={'date': 'DATE_FORMAT(creation_date, "%s")' % sql_format},
                                                  portal_type=portal_type_list,limit=None,
                                                  owner=context.Person_getUserId(),
                                                  group_by=['DATE_FORMAT(creation_date, "%s")' % sql_format],
                                                  **count_kw)

# build result dict per portal_type then period
period_count_dict = {}
for result in result_list:
  period_count_dict[result[1]] = result[0]

# build line
obj = Object(uid="new_")
obj["document_type"] = 'Total'
line_counter = 0
for period in period_list:
  if period_count_dict.has_key(period):
    obj[period] = period_count_dict[period]
    line_counter += period_count_dict[period]
  else:
    obj[period] = 0
obj['total'] = line_counter

return [obj,]
