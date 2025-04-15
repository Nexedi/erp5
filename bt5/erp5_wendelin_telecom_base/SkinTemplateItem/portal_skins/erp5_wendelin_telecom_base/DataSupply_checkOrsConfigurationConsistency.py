data_supply = context

error_list = []

data_acquisition_unit = None
for data_supply_line in data_supply.contentValues(portal_type='Data Supply Line'):
  aggregate_obj = data_supply_line.getAggregateValue(portal_type='Data Acquisition Unit')
  if aggregate_obj is not None:
    data_acquisition_unit = aggregate_obj

if data_acquisition_unit is None:
  error_list.append("Data Supply is not related to a Data Acquisition Unit")
  return error_list

if data_supply.getReference() != data_acquisition_unit.getReference():
  error_list.append("Reference does not match the associated Data Acquisition Unit's reference")

associated_validation_state = data_acquisition_unit.getValidationState()
validation_state = data_supply.getValidationState()
if 'draft' not in [validation_state, associated_validation_state] \
  and validation_state != associated_validation_state:
  error_list.append("Validation state does not match that of the associated Data Acquisition Unit")

return error_list
