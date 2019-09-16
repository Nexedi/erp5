portal = context.getPortalObject()
active_process = portal.restrictedTraverse(active_process_url)
portal.portal_activities.manage_delObjects(
  ids=[active_process.getId(),])
return "Done"
