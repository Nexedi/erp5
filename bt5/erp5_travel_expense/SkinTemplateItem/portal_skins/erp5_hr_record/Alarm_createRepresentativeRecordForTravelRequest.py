portal = context.getPortalObject()
portal.portal_catalog.searchAndActivate(
  portal_type="Travel Request",
  method_id='TravelRequest_createRepresentativeRecord',
  activate_kw={'tag': tag},
)
context.activate(activity='SQLDict', after_tag=tag).getId()
