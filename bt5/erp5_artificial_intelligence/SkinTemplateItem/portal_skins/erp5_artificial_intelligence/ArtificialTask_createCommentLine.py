artificial_task = context

# Starts the gevent-based notification relay background thread, if this
# Zope worker is the one designated to host it (no-op after the first call,
# and a no-op entirely on workers that aren't configured to run it).
#artificial_task.Base_startNotificationRelayIfConfigured()

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
