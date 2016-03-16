"""
  Returns the list of results of the specified process
  or of the last process if nothing specified.
"""

if active_process is None:
  active_process = context.getLastActiveProcess()
else:
  active_process = context.getPortalObject().restrictedTraverse(active_process)

result_list = []

if active_process is not None:
  result_list = [x for x in active_process.getResultList()]
  # High severity will be displayed first
  result_list.sort(key=lambda x: -x.severity)

return result_list
