portal = context.getPortalObject()
form = context.REQUEST.form
event_module = portal.event_module

firstname = context.REQUEST.get('field_your_first_name')

new_event = portal.event_module.newContent(portal_type=portal_type)
new_event.setTitle(firstname)

return new_event.Base_redirect("view")
