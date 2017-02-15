portal = context.getPortalObject()
portal.portal_catalog.searchAndActivate(
  portal_type="Leave Request",
  method_id='LeaveRequest_createRepresentativeRecord',
  activate_kw={'tag': tag},
)
context.activate(after_tag=tag).getId()
