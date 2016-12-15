portal = context.getPortalObject()
portal.portal_catalog.searchAndActivate(
  portal_type="Leave Request Record",
  simulation_state=["draft"],
  method_id='LeaveRequestRecord_processDraftRecord',
)

portal.portal_catalog.searchAndActivate(
  portal_type="Travel Request Record",
  simulation_state=["draft"],
  method_id='Record_processDraftRecord',
)

portal.portal_catalog.searchAndActivate(
  portal_type="Expense Record",
  simulation_state=["draft"],
  method_id='Record_processDraftRecord',
)
