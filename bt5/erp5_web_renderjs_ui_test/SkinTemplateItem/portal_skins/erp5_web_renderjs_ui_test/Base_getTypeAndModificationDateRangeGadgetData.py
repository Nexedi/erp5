translateString = context.Base_translateString

return [
  ("group_by", "portal_type"),
  ("query_by", {"parent_uid": context.getUid()}),
  ("title", translateString("Number of events from a range of modification_date")),
  ("layout", {
    "x": {
      "title": translateString("Days"),
      "key": "getTranslatedPortalType",
      "label_list": ["< 2", "2 - 7", "7 - 30", "> 30"],
      "domain_list": [
        'modification_date_lt2',
        'modification_date_2to7',
        'modification_date_7to30',
        'modification_date_gt30'
      ]
    },
    "y": {
      "title": translateString("Quantity")
    }
  })
]
