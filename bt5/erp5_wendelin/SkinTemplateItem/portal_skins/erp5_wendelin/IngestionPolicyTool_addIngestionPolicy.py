"""
  Create all required types for proper ingestion.
"""
from DateTime import DateTime

now = DateTime()
ingestion_policy = context.newContent( \
      id = reference,
      portal_type ='Ingestion Policy',
      reference = reference,
      version = '001',
      script_id = 'ERP5Site_handleDefaultFluentdIngestion')
ingestion_policy.validate()
    
# create sensor
sensor = context.sensor_module.newContent( \
                            portal_type='Sensor', 
                            reference = reference)
sensor.validate()

# create new Data Stream
data_stream = context.data_stream_module.newContent( \
                   portal_type='Data Stream', \
                   version = '001', \
                   reference=reference)
data_stream.validate()
    
# create Data Supply
resource = context.restrictedTraverse('data_product_module/wendelin_4')
data_supply_kw = {'reference': reference,
                  'version': '001',
                  'start_date': now,
                  'stop_date': now + 365}
data_supply_line_kw = {'resource_value': resource,
                       'source_value': sensor,
                       'destination_value': data_stream}
data_supply = ingestion_policy.PortalIngestionPolicy_addDataSupply( \
                                  data_supply_kw, \
                                  data_supply_line_kw)
    
data_array = context.data_array_module.newContent(
                                        portal_type='Data Array',
                                        reference = reference,
                                        version = '001')
data_array.validate()

if batch_mode:
  return ingestion_policy, data_supply, data_stream, data_array
else:
  # UI case
  ingestion_policy.Base_redirect(\
                    form_id='view', \
                    keep_items={'portal_status_message': \
                      context.Base_translateString('Ingestion Policy added.')})
