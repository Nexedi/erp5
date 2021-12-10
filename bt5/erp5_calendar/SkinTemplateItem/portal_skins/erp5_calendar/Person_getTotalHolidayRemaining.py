if context.getPortalType() == 'Holiday Acquisition':
  node_uid = context.getDestinationUid()
else:
  node_uid = context.getUid()

return context.portal_simulation.getFutureInventory(
  portal_type=("Holiday Acquisition", "Leave Request Period"),
  node_uid=node_uid
)
