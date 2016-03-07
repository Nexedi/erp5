portal = context.getPortalObject()

person_list = portal.portal_catalog(portal_type="Person",
  select_list=['relative_url'],
  validation_state="validated")

message_list = ["%s should be invalidated" % person.relative_url for person in person_list]

if message_list and fixit:
  portal.portal_catalog.searchAndActivate(method_id="invalidate",
    portal_type="Person", validation_state="validated")

return message_list
