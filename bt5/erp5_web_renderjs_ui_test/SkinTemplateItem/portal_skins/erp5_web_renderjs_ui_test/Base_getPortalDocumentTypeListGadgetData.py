translateString = context.Base_translateString

return [
  ("group_by", ["portal_type",]),
  ("query_by", {"portal_type": context.getPortalDocumentTypeList()}),
  ("title", translateString("Number of Documents")),
  ("layout", {
    "x": {
      "title": translateString("Portal Type"),
      "key": "getTranslatedPortalType"
    },
    "y": {
      "title": translateString("Quantity")
    }
  })
]
