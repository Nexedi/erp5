setHeader = context.REQUEST.response.setHeader

setHeader("Access-Control-Allow-Origin", "*")
setHeader("Access-Control-Allow-Methods", "HEAD, OPTIONS, GET, POST")
setHeader("Access-Control-Allow-Headers", "Overwrite, Destination, Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, If-Modified-Since, X-File-Name, Cache-Control, Authorization")
value = container.MonitorBackend_simulatorMapping(path)
if value is not None:
  return value
else:
  return 'OK'
