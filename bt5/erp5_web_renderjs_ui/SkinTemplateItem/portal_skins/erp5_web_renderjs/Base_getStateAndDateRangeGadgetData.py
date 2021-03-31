translateString = context.Base_translateString

domain_id = "graphic_gadget_delivery_start_date_domain"
column_list, domain_list = context.Base_getSubdomainTitleAndIdList(domain_id)

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
      "domain_id": domain_id,
      "column_list": column_list,
      "domain_list": domain_list
    },
    "y": {
      "title": translateString("Quantity")
    }
  })
]
