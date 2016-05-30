if REQUEST is None or form.getId() != "Base_viewListModeRenderer":
  return "%s_%s_selection" % (form.getId(), field.getId())

request_selection_name = REQUEST.get("selection_name")
if request_selection_name:
  selection_parameters = context.portal_selections.getSelectionParamsFor("%s_list_mode_proxy_selection" % request_selection_name)
else:
  selection_parameters = {}

return "%s_%s_selection" % (
  REQUEST.get("proxy_form_id") or
  selection_parameters.get("proxy_form_id") or
  form.getId(),
  REQUEST.get("proxy_field_id") or
  selection_parameters.get("proxy_field_id") or
  field.getId(),
)
