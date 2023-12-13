'''
  Activate this whenever we have a process going wrong and
  we do not want disturb the user or stop (rollback) the process
  but we do want developpers to be notified.
'''
context.getPortalObject().portal_activities.getActivityRuntimeEnvironment().edit(max_retry=0)
raise RuntimeError(error_message)
