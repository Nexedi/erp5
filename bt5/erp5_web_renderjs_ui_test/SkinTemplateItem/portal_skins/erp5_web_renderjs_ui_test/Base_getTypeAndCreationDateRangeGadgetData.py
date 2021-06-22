from urllib import quote

def extract_date(date):
  return quote(date.strftime("%Y-%m-%d"))

translateString = context.Base_translateString

return [
  ("group_by", "portal_type"),
  ("date_range_catalog_key", "creation_date"),
  ("date_range_list", [
    # label, start, end
    ["< 2", extract_date(DateTime()-2), extract_date(DateTime()+1)],
    ["2 - 7", extract_date(DateTime()-7), extract_date(DateTime()-2)],
    ["7 - 30", extract_date(DateTime()-30), extract_date(DateTime()-7)],
    ["> 30", extract_date(DateTime(1900, 1, 1)), extract_date(DateTime()-30)],
  ]),
  ("query_by", "getTranslatedPortalType"),
  ("base_query", {"parent_uid": context.getUid()}),
  ("graph_title", translateString("Number of events from a range of creation_date")),
  ("x_title", translateString("Days"))
]
