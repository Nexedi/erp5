portal = context.getPortalObject()

archived_reference_marker = 'ARCHIVED'

data_acquisition_unit_list = portal.data_acquisition_unit_module.searchFolder(
  portal_type='Data Acquisition Unit',
  validation_state='validated'
)
listbox_item_list = []

for data_acquisition_unit in data_acquisition_unit_list:
  # Already archived or non-validated item: skip it
  if archived_reference_marker in data_acquisition_unit.getReference() \
    or data_acquisition_unit.getValidationState() != 'validated':
    continue

  destination_project = None
  data_supply = data_acquisition_unit.DataAcquisitionUnit_getOrsDataSupply()
  # Non-standard ORS Data Acquisition Unit
  if data_supply is None:
    continue

  destination_project = data_supply.getDestinationProject()

  context_obj = data_acquisition_unit.asContext(
    destination_project=destination_project
  )
  listbox_item_list.append(context_obj)

return listbox_item_list
