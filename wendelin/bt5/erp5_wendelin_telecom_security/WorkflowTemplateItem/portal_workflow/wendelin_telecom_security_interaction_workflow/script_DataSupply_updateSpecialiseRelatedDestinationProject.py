data_supply = state_change['object']

destination_project = data_supply.getDestinationProject()
for value in data_supply.getSpecialiseRelatedValueList(
  portal_type=('Data Analysis', 'Data Analysis Line', 'Data Ingestion')
):
  if value.getSimulationState() == 'started':
    value.setDestinationProject(destination_project)
