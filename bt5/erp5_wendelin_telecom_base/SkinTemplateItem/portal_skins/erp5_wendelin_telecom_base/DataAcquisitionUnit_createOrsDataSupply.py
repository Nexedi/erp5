'''
Creates a pre-configured Data Supply related to a Data Acquisition Unit representing an ORS.

The related Data Supply has the same reference as the Data Acquisition Unit, which is the
ORS's fluentbit tag and is needed for proper ingestion of its logs.
The script first checks if the Data Supply already exists, and will create it if it doesn't.
If batch == 1, the Data Supply object is returned in both cases of the above check.
Otherwise, the user is redirected to the Data Supply's view page.
'''

if not context.getReference():
  if batch:
    return None
  return context.Base_redirect('view', keep_items={
    'portal_status_message': 'Reference is not defined.',
    'portal_status_level': 'error'
  })
reference = context.getReference()

data_supply = context.DataAcquisitionUnit_getOrsDataSupply()
if data_supply:
  if batch:
    return data_supply
  return data_supply.Base_redirect('view', keep_items={
    'portal_status_message': 'Data Supply already exists.'
  })

data_supply = context.data_supply_module.newContent(
  portal_type='Data Supply',
  reference=reference,
  source='organisation_module/open_radio_station',
  source_section='organisation_module/open_radio_station',
  destination='organisation_module/rapid_space_data_center'
)

data_supply.newContent(
  portal_type='Data Supply Line',
  title='Data Stream',
  reference='out_stream',
  quantity=1,
  int_index=2,
  use='big_data/ingestion/stream',
  resource="data_product_module/ors_enb_log_data"
).validate()
data_supply.newContent(
  portal_type='Data Supply Line',
  title='Ingest ORS eNB Log Data',
  reference='ingestion_operation',
  quantity=1,
  int_index=1,
  aggregate_value=context,
  resource='data_operation_module/ingest_ors_enb_log_data'
).validate()

data_supply.validate()

if batch:
  return data_supply
return data_supply.Base_redirect('view', keep_items={
  'portal_status_message': 'Data Supply successfully created.'
})
