if not context.getReference():
  if batch:
    return None
  return context.Base_redirect('view', keep_items={
    'portal_status_message': 'Reference is not defined.',
    'portal_status_level': 'error'
  })
reference = context.getReference()

# XXX DataAcquisitionUnit_getOrsDataSupply is generic enough, it should
# be called DataAcquisitionUnit_getDataSupply or something similar
data_supply = context.DataAcquisitionUnit_getOrsDataSupply()
if data_supply:
  if batch:
    return data_supply
  return data_supply.Base_redirect('view', keep_items={
    'portal_status_message': 'Data Supply already exists.'
  })

# XXX Update me please this is horrible hardcoded for ORS
data_supply = context.data_supply_module.newContent(
  portal_type='Data Supply',
  reference=reference,
  source='organisation_module/cdn_provider',
  source_section='organisation_module/cdn_provider',
  destination='organisation_module/rapid_space_data_center'
)

data_supply.newContent(
  portal_type='Data Supply Line',
  title='Data Stream',
  reference='out_stream',
  quantity=1,
  int_index=2,
  use='big_data/ingestion/stream',
  resource="data_product_module/cdn_access_log_data"
).validate()

data_supply.newContent(
  portal_type='Data Supply Line',
  title='Ingest CDN Access Log Data',
  reference='ingestion_operation',
  quantity=1,
  int_index=1,
  aggregate_value=context,
  resource='data_operation_module/ingest_cdn_access_log_data'
).validate()

data_supply.validate()

if batch:
  return data_supply
return data_supply.Base_redirect('view', keep_items={
  'portal_status_message': 'Data Supply successfully created.'
})
