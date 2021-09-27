maileva_connector = context.portal_catalog.getResultValue(
  reference=reference,
  validation_state='validated')
if not maileva_connector:
  raise ValueError('Maileav soap connector is not defined')
return maileva_connector
