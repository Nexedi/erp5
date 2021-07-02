translateString = context.Base_translateString

return [
  ("group_by", "simulation_state"),
  ("query_by", {"parent_uid": context.getUid()}),
  ("title", translateString(
    "%s Pipes" % context.getPortalType().replace(" Module", "")
  )),
  ("layout", {
    "x": {
      "title": translateString("Days"),
      "key": "getTranslatedSimulationStateTitle",
      "label_list": ["< 2", "2 - 7", "7 - 30", "> 30"],
      "domain_list": [(
        "graphic_gadget_domain", (
          'delivery_start_date_lt2',
          'delivery_start_date_2to7',
          'delivery_start_date_7to30',
          'delivery_start_date_gt30'
        )
      )]
    },
    "y": {
      "title": translateString("Quantity")
    }
  })
]
