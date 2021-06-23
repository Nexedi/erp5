translateString = context.Base_translateString

return [
  ("group_by", "portal_type"),
  ("query_by", "getTranslatedPortalType"),
  ("base_query", {"portal_type": context.getPortalDocumentTypeList()}),
  ("title", translateString("Number of Documents")),
  ("x_title", translateString("Portal Type"))
]
