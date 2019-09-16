"""
  We need proy role as manager to create a new active process
  and post active result
"""
portal = context.getPortalObject()

if REQUEST:
  return RuntimeError("You cannot run this script in the url")

if active_process_url:
  active_process = portal.restrictedTraverse(active_process_url)
else:
  active_process = portal.portal_activities.newActiveProcess()

active_process.postActiveResult(detail=detail)

return active_process
