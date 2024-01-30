"""
  Returns the list of results of the specified process
  or of the last process if nothing specified.
"""

if active_process is None:
  # Get the last active process finished, not the current one.
  active_process = context.getPortalObject().portal_catalog.getResultValue(
    portal_type='Active Process',
    sort_on=(('creation_date', 'DESC'),
             # XXX Work around poor resolution of MySQL dates.
             ('id', 'DESC', 'UNSIGNED')),
    causality_uid=context.getUid())

else:
  active_process = context.getPortalObject().restrictedTraverse(active_process)

if active_process is None:
  return []

return active_process.ActiveProcess_getResultList()
