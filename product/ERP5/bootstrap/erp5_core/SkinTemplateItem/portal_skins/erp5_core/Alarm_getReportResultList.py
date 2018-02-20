"""
  Returns the list of results of the specified process
  or of the last process if nothing specified.
"""

if active_process is None:
  active_process = context.getLastActiveProcess()
else:
  active_process = context.getPortalObject().restrictedTraverse(active_process)

if active_process is None:
  return []

return active_process.ActiveProcess_getResultList()
