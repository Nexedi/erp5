portal = context.getPortalObject()

data_analysis_list = portal.data_analysis_module.searchFolder(
  portal_type='Data Analysis',
  simulation_state='started'
)
listbox_item_list = []

for data_analysis in data_analysis_list:
  # Only allow to refresh analyses that are
  # still ongoing and not still refreshing
  if data_analysis.getSimulationState() == 'started' \
    and data_analysis.getRefreshState() == 'current':
    listbox_item_list.append(data_analysis)

return listbox_item_list
