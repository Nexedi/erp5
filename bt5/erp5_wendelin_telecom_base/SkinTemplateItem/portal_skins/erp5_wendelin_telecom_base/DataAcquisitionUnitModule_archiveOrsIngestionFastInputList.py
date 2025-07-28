from datetime import datetime

portal = context.getPortalObject()

now_date_str = datetime.today().strftime('%Y%m%d-%H%M%S')
archived_reference_suffix = 'ARCHIVED-%s' % now_date_str
archived_title_suffix = 'ARCHIVED %s' % now_date_str

def updateItemReference(item):
  item_reference = item.getReference()
  archived_item_reference = '%s-%s' % (item_reference, archived_reference_suffix)
  item.setReference(archived_item_reference)

def updateItemTitle(item):
  item_title = item.getTitle()
  if item_title != item.getReference():
    archived_item_title = '%s %s' % (item_title, archived_title_suffix)
    item.setTitle(archived_item_title)

def deleteItem(item):
  if item.getValidationState() == 'validated':
    item.invalidate()
  if item.getValidationState() != 'deleted':
    item.delete()

def deliverDataSimulation(data_simulation_item):
  if data_simulation_item.getSimulationState() == 'started':
    data_simulation_item.deliver()

selected_listbox = [
  listbox_item for listbox_item in listbox \
  if listbox_item.get('listbox_selected', False)
]

for selected_item in selected_listbox:
  if 'listbox_key' in selected_item:
    data_acquisition_unit_url = selected_item['listbox_key']

    data_acquisition_unit = portal.restrictedTraverse(
      data_acquisition_unit_url
    )

    data_supply = data_acquisition_unit.DataAcquisitionUnit_getOrsDataSupply()
    # Non-standard ORS Data Acquisition Unit
    if data_supply is None:
      continue
    data_supply_lines = data_supply.contentValues(portal_type='Data Supply Line')

    data_ingestion = None
    for line in data_acquisition_unit.getAggregateRelatedValueList(
      portal_type='Data Ingestion Line'
    ):
      data_ingestion = line.getParentValue()

    data_stream = None
    for line in data_acquisition_unit.getAggregateRelatedValueList(
      portal_type='Data Ingestion Line'
    ):
      data_stream = line.getAggregateValue(portal_type='Data Stream')

    data_analysis = None
    if data_supply is not None:
      data_analysis_list = data_supply.getSpecialiseRelatedValueList(
        portal_type='Data Analysis'
      )
      if len(data_analysis_list) == 1:
        data_analysis = data_analysis_list[0]

    progress_indicator = None
    if data_analysis is not None:
      for line in data_analysis.contentValues(portal_type="Data Analysis Line"):
        if line.getResourceValue().getPortalType() == "Data Product" \
          and line.getQuantity() == -1:
          progress_indicator = line.getAggregateProgressIndicatorValue()

    data_array_list = []
    if data_analysis is not None:
      for line in data_analysis.contentValues(portal_type='Data Analysis Line'):
        data_array = line.getAggregateValue(portal_type='Data Array')
        if data_array is not None:
          data_array_list.append(data_array)

    # Archive Data Acquisition Unit and Data Supply first
    updateItemReference(data_acquisition_unit)
    updateItemTitle(data_acquisition_unit)
    deleteItem(data_acquisition_unit)

    for data_supply_line in data_supply_lines:
      deleteItem(data_supply_line)
      # No need to update reference here
    updateItemReference(data_supply)
    deleteItem(data_supply)

    # Stop ongoing Data Ingestion and Data Analysis next
    if data_ingestion is not None:
      updateItemReference(data_ingestion)
      deliverDataSimulation(data_ingestion)

    if data_analysis is not None:
      updateItemReference(data_analysis)
      deliverDataSimulation(data_analysis)

    # Finally, invalidate Data Stream, Data Arrays and Progress Indicator
    if data_stream is not None:
      updateItemReference(data_stream)
      deleteItem(data_stream)

    for data_array in data_array_list:
      updateItemReference(data_array)
      deleteItem(data_array)

    if progress_indicator is not None:
      # This does not work for some reason
      # updateItemReference(progress_indicator)
      deleteItem(progress_indicator)

return context.Base_redirect('view', keep_items={
  'portal_status_message': 'Selected Data Acquisition Units and related data ingestion successfully archived.'
})
