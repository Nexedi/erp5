"""Resource lister from a ticket
"""
portal = context.getPortalObject()
portal_type = portal.getPortalEventTypeList()[0]

event = portal.getDefaultModule(portal_type).newContent(portal_type=portal_type,
                                                         temp_object=True)

return event.Event_getResourceItemList()
