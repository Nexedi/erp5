translateString = context.Base_translateString

listbox_data_dict = context.Base_extractGadgetDataDictFromListbox(
  context.Base_viewStateAndDateRangeGadgetDataList.listbox
)

return [
  ("group_by", listbox_data_dict["group_by"]),
  ("query_by", listbox_data_dict["query_by"]),
  ("title", listbox_data_dict["title"]),
  ("layout", {
    "x": {
      "title": translateString("Days"),
      "key": "getTranslatedSimulationStateTitle",
      "domain_id": listbox_data_dict["domain_id"],
      "column_list": listbox_data_dict["column_list"],
      "domain_list": listbox_data_dict["domain_list"]
    },
    "y": {
      "title": translateString("Quantity")
    }
  })
]
