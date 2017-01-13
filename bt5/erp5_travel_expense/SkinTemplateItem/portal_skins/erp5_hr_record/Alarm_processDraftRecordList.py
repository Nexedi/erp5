portal = context.getPortalObject()
portal.portal_catalog.searchAndActivate(
  portal_type=(
    "Leave Request Record",
    "Travel Request Record",
    "Expense Record",
    ),
  simulation_state=["draft"],
  method_id='Record_processDraftRecord',
)
