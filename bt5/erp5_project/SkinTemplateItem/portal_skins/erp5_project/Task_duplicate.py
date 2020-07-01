from erp5.component.module.DateUtils import addToDate

task_portal_type = 'Task'
task_module = context.getDefaultModule(task_portal_type)

cb_data = task_module.manage_copyObjects([context.getId()])
copied, = task_module.manage_pasteObjects(cb_data)
pasted_task = task_module[copied['new_id']]

# Get task dates
start_date = pasted_task.getStartDate()
stop_date = pasted_task.getStopDate()
duration = int(stop_date) - int(start_date)
second_to_add = int(next_date) - int(start_date)

for line in pasted_task.getMovementList():
  # Get task line dates
  if line.hasStartDate():
    line_start_date = line.getStartDate()
  else:
    line_start_date = start_date

  if line.hasStopDate():
    line_stop_date = line.getStopDate()
  else:
    line_stop_date = stop_date

  line_duration = int(line_stop_date) - int(line_start_date)
  # Line dates are different from task dates
  next_line_start_date = addToDate(line_start_date, second=second_to_add)
  line.edit(
    start_date=next_line_start_date,
    stop_date=addToDate(next_line_start_date, second=line_duration),
  )

pasted_task.edit(
  start_date=next_date,
  stop_date=addToDate(next_date, second=duration),
)
