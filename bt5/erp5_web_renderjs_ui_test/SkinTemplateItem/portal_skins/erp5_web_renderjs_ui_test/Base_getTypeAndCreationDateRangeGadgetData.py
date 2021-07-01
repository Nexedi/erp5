translateString = context.Base_translateString

return [
  ("group_by", "portal_type"),
  ("query_by", {"parent_uid": context.getUid()}),
  ("title", translateString("Number of events from a range of creation_date")),
  ("layout", {
    "x": {
      "title": translateString("Days"),
      "key": "getTranslatedPortalType",
      "label_list": ["< 2", "2 - 7", "7 - 30", "> 30"],
      "domain_list": [(
        "graphic_gadget_domain", (
          'creation_date_lt2',
          'creation_date_2to7',
          'creation_date_7to30',
          'creation_date_gt30'
        )
      )]
    },
    "y": {
      "title": translateString("Quantity")
    }
  })
]
