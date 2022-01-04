kw['simulation_state'] = 'confirmed'

if context.getPortalType() == 'Holiday Acquisition':
  kw['node_uid'] = context.getDestinationUid()
  kw['at_date'] = context.getStartDate()
else:
  kw["node_uid"]=context.getUid()
kw["portal_type"]=("Holiday Acquisition", "Leave Request Period")
return context.getPortalObject().portal_simulation.getInventoryList(**kw)
