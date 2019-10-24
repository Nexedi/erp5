# Manually force restricted mode in the ERP5Document_getHateoas
# Can not be done quickly with Security handling, as it redirects the request to the login form

new_skin_name = "Hal"
context.getPortalObject().portal_skins.changeSkin(new_skin_name)
if REQUEST is None:
  REQUEST = context.REQUEST
REQUEST.set('portal_skin', new_skin_name)

return context.ERP5Document_getHateoas(
  REQUEST=REQUEST,
  response=response,
  view=view,
  mode=mode,
  query=query,
  select_list=select_list,
  limit=limit,
  form=form,
  form_data=form_data,
  relative_url=relative_url,
  list_method=list_method,
  default_param_json=default_param_json,
  form_relative_url=form_relative_url,
  bulk_list=bulk_list,
  group_by=group_by,
  sort_on=sort_on,
  local_roles=local_roles,
  selection_domain=selection_domain,
  restricted=1,
  extra_param_json=extra_param_json,
  portal_status_message=portal_status_message,
  portal_status_level=portal_status_level,
  keep_items=keep_items
)
