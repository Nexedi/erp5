domain_id = listbox.get_value("domain_root_list")[0][0]
label_list, domain_list = context.Base_getSubdomainTitleAndIdList(domain_id)

default_param_dict = {}

# Use dict() is simpler but is slower
for (key, value) in listbox.get_value('default_params') or []:
  if isinstance(value, list):
    default_param_dict.setdefault(key, []).extend(value)
  else:
    default_param_dict.setdefault(key, []).append(value)

return {
  "title": listbox.get_value("title"),
  "query_by": default_param_dict,
  "group_by": default_param_dict.pop("group_by", []),
  "domain_id": domain_id,
  "label_list": label_list,
  "domain_list": domain_list,
  "column_list": listbox.get_value("columns")
}
