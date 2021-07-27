domain_id = listbox.get_value("domain_root_list")[0][0]
portal = context.getPortalObject()
base_category = getattr(portal.portal_categories, domain_id, None)

if base_category is not None:
  label_list, domain_list = [], []
  # should we get childs recursively?
  for child in base_category.objectValues():
    label_list.append(child.getTranslatedTitle())
    domain_list.append(child.getId())
else:
  label_list, domain_list = context.Base_getSubdomainTitleAndIdList(domain_id)

default_param_dict = {}
default_param_list = listbox.get_value('default_params') or []

if default_param_list:
  list_method, relative_url = None, None
  # Use dict() is simpler but is slower
  for (key, value) in default_param_list:
    if isinstance(value, list):
      default_param_dict.setdefault(key, []).extend(value)
    else:
      default_param_dict.setdefault(key, []).append(value)
else:
  relative_url = context.getObject().getRelativeUrl()
  list_method = listbox.get_value("list_method").getMethodName()

list_method_template = ("%s/ERP5Document_getHateoas?mode=search"
                        "{&query,select_list*,limit*,group_by*,sort_on*,"
                        "local_roles*,selection_domain*,list_method*,relative_url*}") % context.REQUEST["VIRTUAL_URL"]

return [
  ("group_by", listbox.get_value("all_columns")[1][0]),
  ("list_method_template", list_method_template),
  ("list_method", list_method),
  ("relative_url", relative_url),
  ("query_by", default_param_dict),
  ("title", listbox.get_value("title")),
  ("layout", {
    "x": {
      "title": listbox.get_value("all_columns")[0][1],
      "key": listbox.get_value("all_columns")[0][0],
      "domain_id": domain_id,
      "column_list": label_list,
      "domain_list": domain_list
    },
    "y": {
      "title": listbox.get_value("all_columns")[1][1]
    }
  })
]
