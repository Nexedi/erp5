translateString = context.Base_translateString

return [
  ("group_by", ["simulation_state", "portal_type"]),
  ("select_list", ["getTranslatedPortalType", "getTranslatedSimulationStateTitle"]),
  ("query_by", {"parent_uid": context.getUid()}),
  ("title", translateString("Number of different events per simulation state")),
  ("layout", {
    "x": {
      "title": translateString("Types"),
      "key": "getTranslatedPortalType",
    },
    "y": {
      "title": translateString("Quantity")
    }
  })
]
