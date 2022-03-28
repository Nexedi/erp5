maileva_connector = context.portal_catalog.getResultValue(
  portal_type='Maileva SOAP Connector',
  reference=reference,
  validation_state='validated')
if not maileva_connector:
  raise ValueError('Maileav soap connector is not defined')
return maileva_connector
