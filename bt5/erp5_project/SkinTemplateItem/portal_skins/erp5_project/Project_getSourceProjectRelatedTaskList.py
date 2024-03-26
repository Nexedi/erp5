source_project_uid_list = [x.uid for x in context.portal_catalog(
     relative_url='%s/%%' % context.getRelativeUrl())] + [context.getUid()]

from Products.ZSQLCatalog.SQLCatalog import Query

sql_kw = {}
if 'from_date' in kw and kw['from_date'] is not None:
  query_kw = {'delivery.start_date' : kw['from_date'],
              'range' : 'min'}
  sql_kw['delivery.start_date'] = Query(**query_kw)
if 'at_date' in kw and kw['at_date'] is not None:
  query_kw = {'delivery.stop_date' : kw['at_date'],
              'range' : 'ngt'}
  sql_kw['delivery.stop_date'] = Query(**query_kw)
if 'simulation_state' in kw and len(kw['simulation_state']) > 0 :
  sql_kw['simulation_state'] = kw['simulation_state']

task_list = [x.getObject() for x in \
  context.portal_catalog(selection_report=selection_report,
          portal_type='Task',
          source_project_uid = source_project_uid_list,
          **sql_kw)]
task_line_list = []
for task in task_list:
  task_line_list.extend(task.contentValues(portal_type='Task Line'))

return sorted(
  task_line_list,
  key=lambda tl: (tl.hasStartDate(), tl.getStartDate(), tl.getTitle()))
