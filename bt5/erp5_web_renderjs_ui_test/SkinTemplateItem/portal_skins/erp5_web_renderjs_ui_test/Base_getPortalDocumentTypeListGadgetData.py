translateString = context.Base_translateString

return [
  ("group_by", "portal_type"),
  ("query_by", "getTranslatedPortalType"),
  ("base_query", {"portal_type": context.getPortalDocumentTypeList()}),
  ("title", translateString("Number of Documents")),
  ("layout", {
    "x": translateString("Portal Type"),
    "y": translateString("Quantity")
  })
]
