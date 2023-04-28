context.getPortalObject().portal_catalog.searchAndActivate(
  portal_type="Software Publication",
  simulation_state=["draft"],
  method_id='SoftwarePublication_submitSoftwarePublication',
  activate_kw={'tag': tag}
)
context.activate(activity='SQLDict', after_tag=tag).getId()
