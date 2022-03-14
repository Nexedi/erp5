"""Update local roles on ticket and all events related to the ticket.
"""
support_request = state_change['object']
portal = support_request.getPortalObject()

support_request.updateLocalRolesOnSecurityGroups()

portal.portal_catalog.activate(activity='SQLQueue').searchAndActivate(
    portal_type=portal.getPortalEventTypeList(),
    follow_up_uid=support_request.getUid(),
    method_id='updateLocalRolesOnSecurityGroups')
