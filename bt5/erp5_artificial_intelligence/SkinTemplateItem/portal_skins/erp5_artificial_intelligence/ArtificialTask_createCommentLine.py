artificial_task = context
line = artificial_task.newContent(portal_type='Artificial Task Line', text_content=data)

line.deliver()
artificial_task.edit(modification_date = DateTime())

if len(artificial_task.getContributorList(portal_type='Person')) <= 1:
  simulation_state = artificial_task.getSimulationState()
  if simulation_state == 'stopped':
    artificial_task.restart()
  elif simulation_state == 'confirmed':
    artificial_task.start()
return
