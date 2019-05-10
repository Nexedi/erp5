kw = {}
if params is None:
  params = {}

last_active_process = context.getLastActiveProcess()
if not params.get('full', False) and last_active_process is not None:
  # fetch only objects modified since last alarm run
  kw['indexation_timestamp'] = '>= %s' % last_active_process.getStartDate().ISO()

# register active process in order to have "windows" of last indexed objects
context.newActiveProcess().getRelativeUrl()

portal = context.getPortalObject()

kw['portal_type'] = portal.getPortalOpenOrderTypeList()
kw['children_portal_type'] = [ i + " Line" for i in portal.getPortalOpenOrderTypeList()]


portal.portal_catalog.searchAndActivate(
  method_id='OpenOrder_updateSimulation',
  packet_size=1,
  activate_kw={'tag':tag},
  **kw
  )

# make alarm run once at time
context.activate(after_tag=tag).getId()
