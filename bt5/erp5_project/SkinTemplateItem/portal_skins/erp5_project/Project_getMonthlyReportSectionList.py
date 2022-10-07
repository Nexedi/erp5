from Products.ERP5Form.Report import ReportSection
from six.moves import range

request = context.REQUEST

object_dict = {} # it contains required temp object to display the listbox
                 # with the amount of time per worker/month/project line
total_object_dict = {} # this is for listbox with amount of time
                       # per worker/project line

column_list= []
worker_column_list = []
portal = context.getPortalObject()
temp_object_container = portal.project_module.newContent(temp_object=1)

# find all Tasks
inventory_kw = {}
if context.getPortalType() == 'Project':
  inventory_kw['project_uid'] = [x.uid for x in portal.portal_catalog(
     relative_url='%s/%%' % context.getRelativeUrl())] + [context.getUid()]
worker_title_list = request.get('worker_title_list')
if worker_title_list is not None and len(worker_title_list):
  worker_uid_list = [x.uid for x in portal.portal_catalog(
                              portal_type='Person',title=worker_title_list)]
  if len(worker_uid_list):
    inventory_kw['node_uid'] = worker_uid_list

from_date = request.get('from_date', None)
if from_date is None:
  from_date = context.getStartDate()
  request.set('from_date',from_date)
at_date = request.get('at_date', None)
if at_date is None:
  at_date = context.getStopDate()
  request.set('at_date',at_date)
simulation_state_set = set(request.get('simulation_state', []))
full_date_string = "%s-%s -> %s-%s" % (from_date.year(), from_date.month(),
                                    at_date.year(), at_date.month())

result_list = []
# We will use inventory API in order to find all quantities
# Launch report only if we have restrictive parameters in inventory_kw,
# otherwise getInventoryList will take all task reports and this will
# kill the current node
if len(inventory_kw):
  before_confirmed_task_state_set = set(portal.getPortalPlannedOrderStateList() + \
           portal.getPortalDraftOrderStateList())
  task_state_set = simulation_state_set.intersection(before_confirmed_task_state_set)
  if len(task_state_set):
    result_list.extend(portal.portal_simulation.getInventoryList(
                  simulation_state = [x for x in task_state_set],
                  portal_type=['Task Line', 'Simulation Movement'],
                  from_date=from_date,
                  at_date=at_date, **inventory_kw))

  task_report_state_set = simulation_state_set.difference(before_confirmed_task_state_set)
  if len(task_report_state_set):
    result_list.extend(portal.portal_simulation.getInventoryList(
                  simulation_state = [x for x in task_report_state_set],
                  portal_type='Task Report Line',
                  from_date=from_date,
                  at_date=at_date, **inventory_kw))

monthly_worker_quantity_dict = {} # Used to get quantity per month and per worker
                                  # and per project line
monthly_project_to_display_dict = {} # Used to get project urls to display per month
                                     # in the report tree
total_project_to_display_dict = {} # Used to get project urls to display in the summary
total_worker_quantity_dict = {} # Used to get quantity per project line and per worker for
                           # the full period
full_date_total_worker_quantity_dict = \
  total_worker_quantity_dict.setdefault(full_date_string, {})
full_date_total_object_dict = total_object_dict.setdefault(full_date_string, {})
full_date_total_project_to_display_dict = \
  total_project_to_display_dict.setdefault(full_date_string, {})


source_uid_dict = {}
project_uid_dict = {}
project_relative_url_dict = {}

def fillDictWithParentAndChildRelativeUrls(my_dict, document_url):
  if my_dict.get(document_url) is None:
    splitted_document_url = document_url.split('/')
    for x in range(0, len(splitted_document_url)):
      my_dict['/'.join(splitted_document_url[0:x+1])] = 1


def getNextMonthStart(date):
  """
  return the next month date of the param date
  """
  if date.month()==12:
    return DateTime(date.year()+1, date.month(), 1)
  else:
    return DateTime(date.year(), date.month()+1, 1)

for task_line in result_list:
  # initialize some variables
  source_uid = task_line.node_uid
  if source_uid is None:
    # This should not happens, so display an error message
    raise ValueError(context.Base_translateString(
        "This task should have a source : ${task_relative_url}",
        mapping = {'task_relative_url': task_line.getRelativeUrl()}))
  source_dict = source_uid_dict.get(source_uid, None)
  if source_dict is None:
    source_value = task_line.getSourceValue()
    source_dict = {'title': source_value.getTitle(),
                   'relative_url': source_value.getRelativeUrl()}
    source_uid_dict[source_uid] = source_dict
  source_title = source_dict['title']
  source_relative_url = source_dict['relative_url']
  start_date_task = task_line.date
  stop_date_task = task_line.mirror_date

  # create a list with people who works on the task
  current_column = (source_relative_url, source_title)
  if current_column not in worker_column_list:
    worker_column_list.append(current_column)
  project_uid = task_line.project_uid
  project_dict = project_uid_dict.get(project_uid, None)
  if project_dict is None:
    project_value = task_line.getSourceProjectValue()
    project_dict = {'relative_url': project_value.getRelativeUrl(),
                    'title': project_value.getTitle()}
    project_uid_dict[project_uid] = project_dict
    project_relative_url_dict['/'.join(project_value.getRelativeUrl().split('/')[0:2])] = 1
  quantity = - task_line.inventory
  project_relative_url = project_dict['relative_url']
  full_date_total_worker_quantity_dict[source_relative_url] = \
    full_date_total_worker_quantity_dict.get(source_relative_url, 0) + quantity
  if project_relative_url not in full_date_total_object_dict:
    temp_object = temp_object_container.newContent(portal_type = 'Project Line',
                temp_object=1,
                string_index = full_date_string,
                category_list = ['source_project/%s' % project_relative_url])
    full_date_total_object_dict[project_relative_url] = temp_object
  current_temp_object = full_date_total_object_dict[project_relative_url]
  object_quantity = quantity + current_temp_object.getProperty(source_relative_url, 0)
  current_temp_object.setProperty(source_relative_url, object_quantity)

  # diff in day between the begin and the end of the task
  diff_day = stop_date_task - start_date_task + 1

  fillDictWithParentAndChildRelativeUrls(full_date_total_project_to_display_dict,
     project_relative_url)

  timekeeper = start_date_task
  while timekeeper <= stop_date_task :
    next_timekeeper = getNextMonthStart(timekeeper)
    string_index = "%s-%s" % ( timekeeper.year(), timekeeper.month())
    quantity_dict = object_dict.setdefault(string_index, {})

    worker_quantity_dict = monthly_worker_quantity_dict.setdefault(string_index, {})
    project_to_display_dict = monthly_project_to_display_dict.setdefault(string_index, {})
    fillDictWithParentAndChildRelativeUrls(project_to_display_dict, project_relative_url)

    if project_relative_url not in quantity_dict:
      temp_object = temp_object_container.newContent(portal_type = 'Project Line',
                  temp_object=1,
                  string_index = string_index,
                  category_list = ['source_project/%s' % project_relative_url])
      quantity_dict[project_relative_url] = temp_object
    current_temp_object = quantity_dict[project_relative_url]
    current_month_quantity = (min(next_timekeeper,stop_date_task+1) - timekeeper )/ diff_day * quantity
    object_quantity = current_month_quantity + current_temp_object.getProperty(source_relative_url, 0)
    worker_quantity_dict[source_relative_url] = worker_quantity_dict.get(source_relative_url, 0) + current_month_quantity
    current_temp_object.setProperty(source_relative_url, object_quantity)
    timekeeper = next_timekeeper

# Now build temp objects for quantity per month and per worker
summary_dict = {}
for string_index, worker_quantity_dict in monthly_worker_quantity_dict.items():
  temp_object = temp_object_container.newContent(portal_type = 'Project Line',
              temp_object=1,
              string_index = string_index)
  summary_dict[string_index] = temp_object
  for source_relative_url, quantity in worker_quantity_dict.items():
    temp_object.setProperty(source_relative_url, quantity)

# Now build temp objects for quantity per worker
total_summary_dict = {}
for string_index, worker_quantity_dict in total_worker_quantity_dict.items():
  temp_object = temp_object_container.newContent(portal_type = 'Project Line',
              temp_object=1,
              string_index = string_index)
  total_summary_dict[string_index] = temp_object
  for source_relative_url, quantity in worker_quantity_dict.items():
    temp_object.setProperty(source_relative_url, quantity)

column_list.extend(worker_column_list)

selection_name = 'project_monthly_report_selection'
portal.portal_selections.setListboxDisplayMode(request, 'ReportTreeMode',
                                              selection_name=selection_name)

result = []

project_dict = {}
for project_relative_url in project_relative_url_dict.keys():
  project_dict[project_relative_url] = portal.restrictedTraverse(project_relative_url)
param_list = [object_dict, summary_dict, column_list, project_dict,
              monthly_project_to_display_dict, False, full_date_string]

result.append(ReportSection(
              path=context.getPhysicalPath(),
              param_list=param_list,
              method_id='Project_getMonthlyReportContext',
              listbox_display_mode='ReportTreeMode',
              form_id='Project_viewMonthlyReportData'))

param_list = [total_object_dict, total_summary_dict, column_list, project_dict,
              total_project_to_display_dict, True, full_date_string]
result.append(ReportSection(
              path=context.getPhysicalPath(),
              param_list=param_list,
              method_id='Project_getMonthlyReportContext',
              listbox_display_mode='ReportTreeMode',
              form_id='Project_viewMonthlySummaryReportData'))
return result
