from urllib import quote

translateString = context.Base_translateString

type_list = context.getPortalDocumentTypeList()
return [
  ("group_by", "portal_type"),
  ("query_by", "getTranslatedPortalType"),
  ("base_query", " OR ".join(["portal_type:=%s" % quote(p) for p in type_list])),
  ("graph_title", translateString("Number of Documents")),
  ("title", translateString("Portal Type"))
]
