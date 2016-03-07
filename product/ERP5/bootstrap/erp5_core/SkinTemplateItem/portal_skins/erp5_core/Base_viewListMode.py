selection_name = '%s_list_mode_proxy_selection' % proxy_field_selection_name
selection_tool = context.getPortalObject().portal_selections

selection_tool.setSelectionParamsFor(selection_name,
                              dict(proxy_form_id=proxy_form_id,
                                   proxy_field_id=proxy_field_id))

return context.Base_viewListModeRenderer(REQUEST=container.REQUEST)
