portal = context.getPortalObject()
category_tool = portal.portal_categories

request = container.REQUEST
from_date = request.get('from_date', None)
at_date = request.get('at_date', None)
if at_date:
  at_date = at_date.latestTime()

aggregation_level = request.get('aggregation_level', None)
report_group_by = request.get('group_by', None)
# get all category
incoterm = request.get('incoterm', None)
section_category = request.get('section_category', None)
order = request.get('order', None)
delivery_mode = request.get('delivery_mode', None)

catalog_params = {}
line_params = {"portal_type" : line_portal_type}
# get all organisations for the selected section category
if section_category:
  group_uid = category_tool.getCategoryValue(section_category).getUid()
  organisation_uid_list = [x.uid for x in portal.portal_catalog(
                                            portal_type="Organisation",
                                            default_group_uid=group_uid)]
  if report_type == "sale":
    catalog_params['default_source_section_uid'] = organisation_uid_list or -1
    line_params["mirror_section_uid"] = organisation_uid_list or -1
  elif report_type:
    catalog_params['default_destination_section_uid'] = organisation_uid_list or -1
    line_params["section_uid"] = organisation_uid_list or -1
else:
  raise ValueError("Section category must be defined for report")
# add category params if defined
if incoterm not in ('', None):
  incoterm_uid = category_tool.incoterm.restrictedTraverse(incoterm).getUid()
  catalog_params['default_incoterm_uid'] = incoterm_uid
if order not in ('', None):
  order_uid = category_tool.order.restrictedTraverse(order).getUid()
  catalog_params['default_order_uid'] = order_uid
if delivery_mode not in ('', None):
  delivery_mode_uid = category_tool.delivery_mode.restrictedTraverse(delivery_mode).getUid()
  catalog_params['default_delivery_mode_uid'] = delivery_mode_uid

# compute sql params, we group and order by date and portal type
if aggregation_level == "year":
  date_format = "%Y"
elif aggregation_level == "month":
  date_format = "%Y-%m"
elif aggregation_level == "week":
  date_format = "%Y-%U"
elif aggregation_level == "day":
  date_format = "%Y-%m-%d"
else:
  raise ValueError("Unsupported aggregation_level: %s" % aggregation_level)

if from_date is not None and at_date is not None:
  catalog_params['delivery.start_date'] = {
    'range': 'minngt',
    'query': (from_date, at_date),
  }
elif from_date is not None:
  catalog_params['delivery.start_date'] = {
    'range': 'min',
    'query': from_date,
  }
elif at_date is not None:
  catalog_params['delivery.start_date'] = {
    'range': 'ngt',
    'query': at_date,
  }

select_params = {
  "select_dict": {
    'source_section_title': None,
    'destination_section_title': None,
    'start_date': 'delivery.start_date',
  },
}

# sort_on_list = [ ('delivery.destination_section_uid', 'ASC'), ('delivery.start_date','ASC')]

active_process_value = portal.portal_activities.newContent(
  portal_type='Active Process',)
catalog_params.update(select_params)
portal.portal_catalog.activate(tag=tag).searchAndActivate(
  method_id="OrderModule_processOrderStat",
  method_kw = {'active_process' : active_process_value.getPath(),
                'line_params' : line_params,
                'date_format' : date_format,
                'report_type' : report_type,
                'report_group_by' : report_group_by},
  select_method_id = 'OrderModule_filterOrderStatResult',
  activate_kw = {'priority' : 7,
    'tag' : tag,
    },
  # All SQL Params
  portal_type=doc_portal_type,
  simulation_state=simulation_state,
  packet_size=1000,
  **catalog_params
  )

return active_process_value
