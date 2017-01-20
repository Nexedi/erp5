portal = context.getPortalObject()
portal.portal_catalog.searchAndActivate(
  portal_type=(
    "Localisation Record"
    ),
  simulation_state=["draft"],
  method_id='LocalisationRecord_processDraftRecord',
)
