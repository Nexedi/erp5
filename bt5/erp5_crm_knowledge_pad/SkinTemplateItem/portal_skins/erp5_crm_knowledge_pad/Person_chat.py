"""
Create a CRM "Mail Message" to communication between context person and currrent logged in user.
XXX: Real time chat option.
"""
portal = context.getPortalObject()
translate = context.Base_translateString

new_event = portal.event_module.newContent(portal_type="Mail Message")
new_event.setDestinationValue(context)
new_event.setSourceValue(portal.portal_membership.getAuthenticatedMember().getUserValue())
portal_status_message = translate("Real time chat will be available soon. Please use email instead.")

return new_event.Base_redirect("view", \
                               keep_items = {'portal_status_message': portal_status_message})
