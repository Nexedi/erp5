request = context.REQUEST

if selection_name is None:
  selection_name = request.get('listbox_list_selection_name')

ps = context.portal_selections
ps.setSelectionToAll(selection_name, REQUEST=request, reset_domain_tree=True, reset_report_tree=True)
ps.setSelectionSortOrder(selection_name, [])
url = ps.getSelectionListUrlFor(selection_name, REQUEST=request)
request.RESPONSE.redirect(url)
