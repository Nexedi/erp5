project_title = context.getTitle()
portal_type='Task Report'

state_list = ['confirmed']
if (closed):
  state_list = ['delivered', 'stopped', 'draft']

from DateTime import DateTime
now = DateTime()
now_minus_7 = now - 7
catalog_kw = {'creation_date': {'query': (now_minus_7, now), 'range': 'minmax'}}
task_list = [x for x in context.portal_catalog(portal_type=portal_type,
                                              source_project_title=project_title,
                                              #simulation_state=state_list,
                                              simulation_state='draft',
                                              **catalog_kw)]

'''
print task_list
for x in task_list:
  print x.getTitle()

return printed
'''
if not task_list:
  return "0"
count = len(task_list)
return count
