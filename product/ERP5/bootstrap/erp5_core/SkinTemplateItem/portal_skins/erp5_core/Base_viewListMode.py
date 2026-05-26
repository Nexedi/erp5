portal = context.getPortalObject()

if proxy_field_selection_name is None:
  portal.REQUEST.RESPONSE.setStatus(400, lock=True)
  return ''

selection_name = '%s_list_mode_proxy_selection' % proxy_field_selection_name
selection_tool = portal.portal_selections

selection_tool.setSelectionParamsFor(selection_name,
                              dict(proxy_form_id=proxy_form_id,
                                   proxy_field_id=proxy_field_id))

return context.Base_viewListModeRenderer(REQUEST=container.REQUEST)
