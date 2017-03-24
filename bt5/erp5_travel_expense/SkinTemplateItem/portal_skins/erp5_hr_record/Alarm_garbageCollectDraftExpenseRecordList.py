portal = context.getPortalObject()
portal.portal_catalog.searchAndActivate(
  portal_type=(
    "Expense Record",
    ),
  simulation_state=["draft"],
  method_id='ExpenseRecord_garbageCollectDraftRecord',
)
