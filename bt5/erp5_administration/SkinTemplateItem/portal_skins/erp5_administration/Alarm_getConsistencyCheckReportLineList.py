"""
  Returns the list of results of the specified process
  or of the last process if nothing specified.
"""

if active_process is None:
  active_process = context.getLastActiveProcess(include_active=True)
else:
  active_process = context.getPortalObject().restrictedTraverse(active_process)

if active_process is None:
  return []

constraint_message_list = []
for result in active_process.ActiveProcess_getResultList():
  constraint_message_list.extend(result.getProperty('constraint_message_list') or [])

return constraint_message_list
