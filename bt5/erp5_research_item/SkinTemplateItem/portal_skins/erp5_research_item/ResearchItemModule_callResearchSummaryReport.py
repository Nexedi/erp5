inventory_kw = {}
if multiplier in (None, ''):
  multiplier = 1.0
inventory_kw["at_date"] = at_date
inventory_kw["from_date"] = from_date
inventory_kw["quantity"] = "<0"
if ledger:
  inventory_kw["ledger"] = "ledger/%s" % ledger
if multiplier is None:
  multiplier = 1

portal = context.getPortalObject()
simulation_state_set = set(simulation_state_list)
# We will use inventory API in order to find all quantities
before_confirmed_task_state_set = set(portal.getPortalPlannedOrderStateList() + \
         portal.getPortalDraftOrderStateList())
task_state_set = simulation_state_set.intersection(before_confirmed_task_state_set)
result_list = []
if len(task_state_set):
  result_list.extend(portal.portal_simulation.getInventoryList(
                simulation_state = [x for x in task_state_set],
                portal_type=['Task Line'],
                **inventory_kw))
task_report_state_set = simulation_state_set.difference(before_confirmed_task_state_set)
if len(task_report_state_set):
  result_list.extend(portal.portal_simulation.getInventoryList(
                simulation_state = [x for x in task_report_state_set],
                portal_type='Task Report Line',
                **inventory_kw))

summary_dict = {}
total_project_dict = {}
item_url_set = set()
for x in result_list:
  aggregate_url = x.sub_variation_text
  item_url = None
  if aggregate_url:
    if aggregate_url.startswith("aggregate"):
      item_url = aggregate_url.split("aggregate/")[1]
  if item_url is None:
    item_url = "None"
  item_url_set.add(item_url)
  person_uid = x.node_uid
  person_dict = summary_dict.setdefault(person_uid, {})
  person_dict[item_url] = x.quantity * multiplier + person_dict.get(item_url, 0)
  person_dict["total"] = x.quantity * multiplier + person_dict.get("total", 0)
  total_project_dict[item_url] = x.quantity * multiplier + total_project_dict.get(item_url, 0)
  total_project_dict["total"] = x.quantity * multiplier + total_project_dict.get("total", 0)

# now we group all results per person and we prepare one line in the listbox
# per person.
person_title_dict = {}
listbox_line_list = []
def getColumnUrl(brain=None, column_id=None, **kw):
  return getattr(brain, "%s_column_url" % column_id)

absolute_url = portal.absolute_url()

if len(summary_dict):
  for person in portal.portal_catalog(portal_type=("Person", "Organisation"), uid=list(summary_dict.keys()), select_list=["title"]):
    person_title_dict[person.uid] = person.title
  for person_uid in summary_dict.keys():
    person_kw = summary_dict[person_uid]
    person_kw["source_title"] = person_title_dict[person_uid]
    person = portal.person_module.newContent(temp_object=1, **person_kw)
    for item_url in summary_dict[person_uid].keys():
      task_report_module_url = "%s/task_report_module/view?reset:int=1&default_source_uid=%s&title=%%" % (absolute_url, person_uid)
      if item_url == "None":
        task_report_module_url += "&child_aggregate_relative_url=%%3dNULL&left_join_list=child_aggregate_relative_url&ledger_relative_url=ledger/%s" % \
                     (ledger, )
      else:
        task_report_module_url += "&child_aggregate_relative_url=%s&ledger_relative_url=ledger/%s" % \
                     (item_url, ledger)
      person.edit(**{"%s_column_url" % item_url: task_report_module_url})
    person.setProperty("getColumnUrl", getColumnUrl)
    listbox_line_list.append(person)

listbox_line_list.sort(key=lambda x: x.getProperty("source_title"))
# now add an extra line for total
person = portal.person_module.newContent(temp_object=1, source_title="Total", **total_project_dict)
listbox_line_list.append(person)

item_title_dict = {}
if item_url_set:
  for item in portal.portal_catalog(portal_type="Research Item", relative_url=list(item_url_set), select_list=["title","relative_url"]):
    item_title_dict[item.relative_url] = item.title
  item_title_dict["None"] = "undefined"

# define which property to display in columns
column_list = [("source_title", "Worker"),
                ("None", "Undefined"), ]
for item_url, item_title in sorted(item_title_dict.items(), key=lambda url_title: url_title[1]):
  if item_url != 'None':
    column_list.append((item_url, item_title))
column_list.append(("total", "Total"))

# define which script to display url in columns
column_url_script_list = []
for item_url in item_title_dict.keys():
  column_url_script_list.append((item_url, "getColumnUrl"))

context = context.asContext(column_list=column_list,
                            at_date=at_date,
                            from_date=from_date,
                            simulation_state_list=simulation_state_list,
                            column_url_script_list=column_url_script_list,
                            ledger=ledger,
                            multiplier=multiplier,
                            listbox_line_list=listbox_line_list)

if batch_mode:
  return context
return context.ResearchItemModule_viewResearchSummaryReportData()
