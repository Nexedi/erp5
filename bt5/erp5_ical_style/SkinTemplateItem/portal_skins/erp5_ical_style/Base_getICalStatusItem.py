"""
  Give an ICal status and percent-completed for a todo entry and status for a event entry.
  Return a tuple of (status, percent_complete).
  For todo status is one of: 'needs-action', 'in-process', 'completed' and 'cancelled' or nothing,
  then we'll assume it is 'needs-action'.
  For event status is one of: 'cancelled', 'confirmed', 'tentative' or nothing,
  then we'll assume it is 'tentative'.
"""
status = ''
status_map_task = {
  'draft' : ('needs-action', 0),
  'planned' : ('needs-action', 33),
  'ordered' : ('in-process', 66),
  'confirmed' : ('completed', 100),
  'cancelled' : ('cancelled', 0)
}

status_map_event = {
  'CANCELLED' : ('expired', 'deleted', 'cancelled'),
  'CONFIRMED' : ('started', 'responded', 'delivered', 'assigned', 'acknowledged'),
  'TENTATIVE' : ('draft', 'planned', 'new', 'ordered')
}

if brainObject is not None:
  real_context = brainObject
else:
  real_context = context

portal_type = real_context.getPortalType()
if portal_type == 'Task':
  return status_map_task.get(real_context.getSimulationState(), ('', 0))
elif portal_type in context.getPortalEventTypeList():
  for status_item in status_map_event:
    if real_context.getSimulationState() in status_map_event[status_item]:
      status = status_item
      break
return (status, 0)
