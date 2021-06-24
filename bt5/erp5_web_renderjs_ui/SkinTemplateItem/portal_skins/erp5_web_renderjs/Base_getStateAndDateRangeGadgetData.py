from urllib import quote

def extract_date(date):
  return quote(date.strftime("%Y-%m-%d"))

translateString = context.Base_translateString

return [
  ("group_by", "simulation_state"),
  ("date_range_catalog_key", "delivery.start_date"),
  ("date_range_list", [
    # label, start, end
    ["< 2", extract_date(DateTime()-2), extract_date(DateTime()+1)],
    ["2 - 7", extract_date(DateTime()-7), extract_date(DateTime()-2)],
    ["7 - 30", extract_date(DateTime()-30), extract_date(DateTime()-7)],
    ["> 30", extract_date(DateTime(1900, 1, 1)), extract_date(DateTime()-30)],
  ]),
  ("query_by", "getTranslatedSimulationStateTitle"),
  ("base_query", {"parent_uid": context.getUid()}),
  ("title", translateString(
    "%s Pipes" % context.getPortalType().replace(" Module", "")
  )),
  ("layout", {
    "x": translateString("Days"),
    "y": translateString("Quantity")
  })
]
