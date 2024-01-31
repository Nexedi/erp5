from Products.PythonScripts.standard import Object
from erp5.component.module.DateUtils import atTheEndOfPeriod
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
count_kw = {}
if from_date is not None and to_date is not None:
  count_kw['creation_date'] = {
    'range': 'minmax',
    'query': (from_date, to_date),
  }
elif from_date is not None:
  count_kw['creation_date'] = {
    'range': 'min',
    'query': from_date,
  }
elif to_date is not None:
  count_kw['creation_date'] = {
    'range': 'max',
    'query': to_date,
  }

# count number of object created by the user for each type of document
reference = kw.get('person_reference_list', context.Person_getUserId())
result_list = context.portal_catalog.countResults(select_dict={'date': 'DATE_FORMAT(creation_date, "%s")' % sql_format, 'portal_type': None},
                                                  portal_type=portal_type_list,limit=None,
                                                  owner=reference,
                                                  group_by=['DATE_FORMAT(creation_date, "%s")' % sql_format, 'portal_type'],
                                                  **count_kw)

# build result dict per portal_type then period
portal_type_count_dict = {}
for result in result_list:
  if result[2] in portal_type_count_dict:
    portal_type_count_dict[result[2]][result[1]] = result[0]
  else:
    portal_type_count_dict[result[2]] = {result[1]:result[0]}

# now filled the listbox with count results
line_list = []
append = line_list.append
period_count_dict = {}
for portal_type in portal_type_list:
  if portal_type in portal_type_count_dict:
    period_count = portal_type_count_dict[portal_type]
    obj = Object(uid="new_")
    obj["document_type"] = context.Base_translateString(portal_type)
  else:
    continue
  line_counter = 0
  for period in period_list:
    if period in period_count:
      obj[period] = period_count[period]
      line_counter += period_count[period]
      if period in period_count_dict:
        period_count_dict[period] = period_count_dict[period] + period_count[period]
      else:
        period_count_dict[period] = period_count[period]
    else:
      obj[period] = 0
  obj['total'] = line_counter
  append(obj)

line_list.sort(key=lambda a:a['document_type'])

# build stat line
obj = Object(uid="new_")
obj["document_type"] = 'Total'
line_counter = 0
for period in period_list:
  if period in period_count_dict:
    obj[period] = period_count_dict[period]
    line_counter += period_count_dict[period]
  else:
    obj[period] = 0
obj['total'] = line_counter
request.set('stat_line', [obj,])

return line_list
