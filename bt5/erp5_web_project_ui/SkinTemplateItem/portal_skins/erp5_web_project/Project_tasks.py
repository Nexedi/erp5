project_title = context.getTitle()
portal_type='Task'

state_list = ['confirmed']

task_list = [x for x in context.portal_catalog(portal_type=portal_type,
                                               source_project_title=project_title,
                                               simulation_state=state_list)]

if not task_list:
  return "0"
count = len(task_list)
return count
