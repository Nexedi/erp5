setHeader = context.REQUEST.response.setHeader
setHeader("Access-Control-Allow-Origin", "*")
setHeader("Access-Control-Allow-Methods", "HEAD, OPTIONS, GET, POST")
setHeader("Access-Control-Allow-Headers", "Overwrite, Destination, Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, If-Modified-Since, X-File-Name, Cache-Control, Authorization")
PATH = context.REQUEST['PATH_INFO']
if '/simulator' in PATH:
  real, simulator = PATH.split('simulator')
  container.REQUEST.set('PATH_INFO', real)
  container.REQUEST.set('SIMULATOR_PATH', simulator)
  container.REQUEST.set('SCRIPT_NAME', 'MonitorBackend_simulator')
  container.REQUEST.set('TraversalRequestNameStack', ['MonitorBackend_simulator'])
