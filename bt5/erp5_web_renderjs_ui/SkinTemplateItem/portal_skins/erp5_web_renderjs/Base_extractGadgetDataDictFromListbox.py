domain_id = listbox.get_value("domain_root_list")[0][0]
portal = context.getPortalObject()
base_category = getattr(portal.portal_categories, domain_id, None)

# We should not group by catalog keys like translate_*_title.
# For now, we keep a dict here, to convert this key by another faster catalog ket
perfomance_mapping = {
  "translated_simulation_state_title": "simulation_state"
}

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

group_by, group_by_title = None, ""

column_list = listbox.get_value("columns") or []
for column in column_list:
  key, title = column
  if any([i in key for i in ("validation_state", "simulation_state")]):
    group_by = key
    group_by_title = title


assert group_by, "group_by not found"

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

# XXX - hack to build absolute_url to add hateoas script through hateoas web site
script_id = "ERP5Document_getHateoas"
root_url = context.getWebSiteValue().hateoas.absolute_url()
list_method_template = (
  "%(root_url)s/%(script_id)s?mode=search"
  "{&query,select_list*,limit*,group_by*,sort_on*,"
  "local_roles*,selection_domain*,list_method*,relative_url*}") % {"root_url": root_url, "script_id": script_id}

return [
  ("group_by", perfomance_mapping.get(group_by, None) or group_by),
  ("list_method_template", list_method_template),
  ("list_method", list_method),
  ("relative_url", relative_url),
  ("query_by", default_param_dict),
  ("title", listbox.get_value("title")),
  ("layout", {
    "x": {
      "title": group_by_title,
      "key": group_by,
      "domain_id": domain_id,
      "column_list": label_list,
      "domain_list": domain_list
    },
    "y": {
      "title": "Quantity"
    }
  })
]
