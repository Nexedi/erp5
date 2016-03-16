source_project_uid_list = [x.uid for x in context.portal_catalog(
     relative_url='%s/%%' % context.getRelativeUrl())] + [context.getUid()]

from Products.ZSQLCatalog.SQLCatalog import Query

sql_kw = {}
if kw.has_key('from_date') and kw['from_date'] is not None:
  query_kw = {'delivery.start_date' : kw['from_date'],
              'range' : 'min'}
  sql_kw['delivery.start_date'] = Query(**query_kw)
if kw.has_key('at_date') and kw['at_date'] is not None:
  query_kw = {'delivery.stop_date' : kw['at_date'],
              'range' : 'ngt'}
  sql_kw['delivery.stop_date'] = Query(**query_kw)

# Make sure to not include "confirmed tasks" in any case, because in
# this case we must take task reports
if kw.has_key('simulation_state') and len(kw['simulation_state']) > 0 :
  task_simulation_state = [x for x in kw['simulation_state'] if x != 'confirmed']
  task_report_simulation_state = kw['simulation_state']
else:
  task_simulation_state = context.getPortalDraftOrderStateList() + \
                          context.getPortalPlannedOrderStateList()
  task_report_simulation_state = ""

task_list = [x.getObject() for x in \
  context.portal_catalog(selection_report=selection_report, 
                         portal_type='Task',
                         source_project_uid = source_project_uid_list,
                         simulation_state = task_simulation_state,
                         **sql_kw)]
task_list.extend([x.getObject() for x in \
  context.portal_catalog(selection_report=selection_report, 
                         portal_type='Task Report',
                         source_project_uid = source_project_uid_list,
                         simulation_state = task_report_simulation_state,
                         **sql_kw)])
task_line_list = []
for task in task_list:
  task_line_list.extend(task.objectValues(portal_type=('Task Line', 'Task Report Line')))


def sortTaskLine(a, b):
  result = cmp(a.getStartDate(), b.getStartDate())
  if result == 0:
    result = cmp(a.getTitle(), b.getTitle())
  return result

task_line_list.sort(sortTaskLine)

return task_line_list
