portal = context.getPortalObject()
event_portal_type_list = portal.getPortalEventTypeList()

for i in portal.portal_catalog(portal_type=event_portal_type_list,
                               follow_up_uid=context.getUid()):
  i.activate().updateLocalRolesOnSecurityGroups()
