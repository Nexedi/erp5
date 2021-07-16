translateString = context.Base_translateString

domain_id = "graphic_gadget_modification_date_domain"
column_list, domain_list = context.Base_getSubdomainTitleAndIdList(domain_id)

return [
  ("group_by", ["portal_type",]),
  ("query_by", {"parent_uid": context.getUid()}),
  ("title", translateString("Number of events from a range of modification_date")),
  ("layout", {
    "x": {
      "title": translateString("Days"),
      "key": "getTranslatedPortalType",
      "domain_id": domain_id,
      "column_list": column_list,
      "domain_list": domain_list
    },
    "y": {
      "title": translateString("Quantity")
    }
  })
]
