path = container.REQUEST['SIMULATOR_PATH']
value = container.MonitorBackend_simulatorMapping(path)
if value is not None:
  return value
else:
  return 'OK'
