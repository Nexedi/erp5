kw_query = {
  "portal_type" : ("Holiday Acquisition", "Leave Request Period"),
  "simulation_state": "confirmed"
}
if context.getPortalType() == 'Holiday Acquisition':
  kw_query["node_uid"] = context.getDestinationUid()
  kw_query['at_date'] = context.getStartDate()
else:
  kw_query["node_uid"] = context.getUid()

return context.portal_simulation.getInventory(**kw_query)
