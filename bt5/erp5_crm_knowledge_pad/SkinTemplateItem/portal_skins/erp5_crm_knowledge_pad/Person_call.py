"""
Create a CRM "Phone Call" to communication between context person and currrent logged in user.
"""
portal = context.getPortalObject()

new_event = portal.event_module.newContent(portal_type="Phone Call")
new_event.setDestinationValue(context)
new_event.setSourceValue(portal.portal_membership.getAuthenticatedMember().getUserValue())

return new_event.Base_redirect("view")
