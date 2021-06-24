translateString = context.Base_translateString

return [
  ("group_by", ["simulation_state", "portal_type"]),
  ("select_list", ["getTranslatedPortalType", "getTranslatedSimulationStateTitle"]),
  ("base_query", {"parent_uid": context.getUid()}),
  ("title", translateString("Number of different events per simulation state")),
  ("layout", {
    "x": translateString("Types"),
    "y": translateString("Quantity")
  })
]
