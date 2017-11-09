tab_list = context.ERP5Site_getTabList()
if tab_list:
  # Obtain the selected tab from the request. This is typically a cookie.
  selected_tab = context.REQUEST.get('erp5_site_selected_tab', None)
  for tab in tab_list:
    if tab['id'] == selected_tab:
      break
  else:
    # If not matched, use the first one.
    tab = tab_list[0]
else:
  tab = None

# Renew a cookie, if possible.
if tab is not None:
  context.REQUEST.RESPONSE.setCookie('erp5_site_selected_tab', tab['id'])

return tab
