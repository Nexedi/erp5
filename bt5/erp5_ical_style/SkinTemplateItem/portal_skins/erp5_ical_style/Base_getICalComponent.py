"""
  Figure out if it is an journal, event or a todo.
  Sample implementation: Task is a todo, event is an event,
  anything else is an journal.
"""
portal_type = None
if brainObject is not None:
  portal_type = brainObject.getPortalType()
else:
  portal_type = context.getPortalType()

if portal_type == 'Task':
  return 'todo'
elif portal_type in context.getPortalEventTypeList():
  return 'event'
return 'journal'
