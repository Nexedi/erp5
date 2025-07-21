portal = context.getPortalObject()

selected_listbox = [
  listbox_item for listbox_item in listbox \
  if listbox_item.get('listbox_selected', False)
]

for selected_item in selected_listbox:
  if 'listbox_key' in selected_item:
    data_analysis_url = selected_item['listbox_key']

    data_analysis = portal.restrictedTraverse(
      data_analysis_url
    )
    if data_analysis.getSimulationState() == 'started' \
      and data_analysis.getRefreshState() == 'current':
      data_analysis.planRefresh()

return context.Base_redirect('view', keep_items={
  'portal_status_message': 'Selected Data Analyses have been successfully planned to refresh.'
})
