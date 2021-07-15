listbox_data_dict = context.Base_extractGadgetDataDictFromListbox(
  context.Base_viewStateAndDateRangeGadgetDataList.listbox
)

return [
  ("group_by", listbox_data_dict["group_by"]),
  ("query_by", listbox_data_dict["query_by"]),
  ("title", listbox_data_dict["title"]),
  ("layout", {
    "x": {
      "title": listbox_data_dict["column_list"][0][1],
      "key": listbox_data_dict["column_list"][0][0],
      "domain_id": listbox_data_dict["domain_id"],
      "column_list": listbox_data_dict["label_list"],
      "domain_list": listbox_data_dict["domain_list"]
    },
    "y": {
      "title": listbox_data_dict["column_list"][1][1]
    }
  })
]
