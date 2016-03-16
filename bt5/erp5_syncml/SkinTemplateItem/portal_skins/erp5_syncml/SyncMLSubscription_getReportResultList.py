"""
  Returns the list of results of the specified process
  or of the last process if nothing specified.
"""

def getLastActiveProcess(sub):
  """
  This returns the last active process finished. So it will
  not returns the current one
  """
  limit = 1
  active_process_list = context.getPortalObject().portal_catalog(
    portal_type='Active Process', limit=limit,
    sort_on=(('creation_date', 'DESC'),
             # XXX Work around poor resolution of MySQL dates.
             ('CONVERT(`catalog`.`id`, UNSIGNED)', 'DESC')),
    causality_uid=sub.getUid())
  if len(active_process_list) < limit:
    process = None
  else:
    process = active_process_list[-1].getObject()
  return process


if active_process is None:
  active_process = getLastActiveProcess(context)
else:
  active_process = context.getPortalObject().restrictedTraverse(active_process)

result_list = []

if active_process is not None:
  result_list = [x for x in active_process.getResultList()]
  # High severity will be displayed first
  result_list.sort(key=lambda x: -x.severity)

return result_list
