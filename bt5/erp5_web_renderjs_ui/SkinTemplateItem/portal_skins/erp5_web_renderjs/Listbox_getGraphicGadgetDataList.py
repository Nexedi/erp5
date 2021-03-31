return context.get_value("field_domain_tree")
data_dict = {
#  ("group_by", "simulation_state"),
#  ("query_by", {"parent_uid": context.getUid()}),
  "title": context.get_value("title"),
  "layout": {
    "x": {
#      "title": translateString("Days"),
#      "key": "getTranslatedSimulationStateTitle",
#      "domain_id": domain_id,
#      "column_list": column_list,
#      "domain_list": domain_list
    },
    "y": {
#      "title": translateString("Quantity")
    }
  }
}

if context.get_value("field_domain_tree"):
  domain_id = context.get_value("field_domain_root_list")[0][0]
  column_list, domain_list = context.Base_getSubdomainTitleAndIdList(domain_id)
  data_dict["layout"]["x"]["column_list"] = column_list
  data_dict["layout"]["x"]["domain_list"] = domain_list

return data_dict.items()
