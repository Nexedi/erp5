context_obj = context.getObject()

module_type   = 'Task Module'
document_type = 'Task'
source_project_type = [ 'Project Line' , 'Project']

task_module = context.getDefaultModule(module_type)

if context_obj.getPortalType() not in source_project_type:
  return context.Base_redirect('view', keep_items={'portal_status_message': 'Error: bar context.'})

# this list contain all task items
task_items = []

# get the user information
for task in listbox:
  if 'listbox_key' in task:
    task_id = int(task['listbox_key'])
    task_dict = {}
    task_dict['id'] = task_id
    task_dict['title'] = task['task_title']
    task_dict['reference'] = task['task_reference']
    task_dict['description'] = task['task_description']
    task_dict['start_date'] = task['task_start_date']
    task_dict['stop_date'] = task['task_stop_date']
    task_dict['requirement'] = task['task_requirement']
    task_dict['source'] = task['task_source'] or source
    task_dict['source_section'] = source_section
    task_dict['resource'] = task['task_line_resource'] or resource
    task_dict['quantity'] = task['task_line_quantity']
    task_dict['quantity_unit'] = task['task_line_quantity_unit'] or task_line_quantity_unit
    task_dict['source_section'] = source_section
    task_dict['destination_decision'] = destination_decision
    task_dict['destination_section'] = destination_section
    task_dict['destination'] = destination
    task_items.append(task_dict)

# sort the requirements list by id to have the same order of the user
task_items.sort(key=lambda x: x['id'])



for item in task_items:

  if item['title'] != '':
    task = task_module.newContent( portal_type = document_type
                                     , title = item['title']
                                     , reference = item['reference']
                                     , description = item['description']
                                     , start_date = item['start_date']
                                     , stop_date = item['stop_date']
                                     , source = item['source']
                                     , source_section = item['source_section']
                                     , resource = item['resource']
                                     , task_line_quantity = item['quantity']
                                     , task_line_quantity_unit = item['quantity_unit']
                                     , destination_decision = item['destination_decision']
                                     , destination_section = item['destination_section']
                                     , destination = item['destination']
                                     )

    if item['reference'] == '':
      task.setReference('T-' + str(task.getId()))

    if item['requirement'] is not None:
      if isinstance(item['requirement'],str):
        task.setTaskLineRequirement(item['requirement'])
      else:
        task.setTaskLineRequirementList(item['requirement'])
    task.setSourceProjectValue(context_obj)

# return to the project
return context.Base_redirect('view', keep_items={'portal_status_message': 'Tasks added at Task Module.'})
