from Products.PythonScripts.standard import Object
from Products.ZSQLCatalog.SQLCatalog import Query
from Products.ERP5Type.DateUtils import atTheEndOfPeriod
request = container.REQUEST
from_date = request.get('from_date', None)
to_date = request.get('at_date', None)
aggregation_level = request.get('aggregation_level', None)
portal = context.getPortalObject()
module_list = []
for module_id in portal.objectIds(spec=('ERP5 Folder',)):
    module = portal.restrictedTraverse(module_id, None)
    if module is not None:
      if portal.portal_membership.checkPermission('View', module):
        module_list.append(module)
module_list.sort(key=lambda x: x.getTitle())

# build document portal type list
portal_type_list = []
extend = portal_type_list.extend
for module in module_list:
  extend(module.ERP5Folder_getUnrestrictedContentTypeList())

# compute sql params, we group and order by date and portal type
if aggregation_level == "year":
  sql_format = "%Y"
elif aggregation_level == "month":
  sql_format = "%Y-%m"
elif aggregation_level == "week":
  sql_format = "%Y-%u"
elif aggregation_level == "day":
  sql_format = "%Y-%m-%d"
if to_date is not None:
  to_date = atTheEndOfPeriod(to_date, period=aggregation_level)
params = {"creation_date":(from_date, to_date)}
query=None
if from_date is not None and to_date is not None:
  params = {"creation_date":(from_date, to_date)}
  query = Query(range="minmax", **params)
elif from_date is not None:
  params = {"creation_date":from_date}
  query = Query(range="min", **params)
elif to_date is not None:
  params = {"creation_date":to_date}
  query = Query(range="max", **params)
select_expression = {'date' : 'DATE_FORMAT(creation_date, "%s")'%sql_format, 'portal_type' : None}
group_by = ['DATE_FORMAT(creation_date, "%s")' % sql_format, 'portal_type']

# count number of object created by the user for each type of document
reference = kw.get('person_reference_list', context.getReference())
result_list = context.portal_catalog.countResults(select_expression=select_expression,
                                                  portal_type=portal_type_list,limit=None,
                                                  owner=reference,query=query,
                                                  group_by_expression=group_by)

# build result dict per portal_type then period
portal_type_count_dict = {}
for result in result_list:
  if portal_type_count_dict.has_key(result[2]):
    portal_type_count_dict[result[2]][result[1]] = result[0]
  else:
    portal_type_count_dict[result[2]] = {result[1]:result[0]}

# now filled the listbox with count results
line_list = []
append = line_list.append
period_count_dict = {}
for portal_type in portal_type_list:
    if portal_type_count_dict.has_key(portal_type):
      period_count = portal_type_count_dict[portal_type]
      obj = Object(uid="new_")
      obj["document_type"] = context.Base_translateString(portal_type)
    else:
      continue
    line_counter = 0
    for period in period_list:
      if period_count.has_key(period):
        obj[period] = period_count[period]
        line_counter += period_count[period]
        if period_count_dict.has_key(period):
          period_count_dict[period] = period_count_dict[period] + period_count[period]
        else:
          period_count_dict[period] = period_count[period]
      else:
        obj[period] = 0
    obj['total'] = line_counter
    append(obj)

# sort lines
def cmpType(a, b):
  return cmp(a['document_type'], b['document_type'])

line_list.sort(cmpType)

# build stat line
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
request.set('stat_line', [obj,])

return line_list
