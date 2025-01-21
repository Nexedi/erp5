maileva_connector_list = context.portal_catalog(
  portal_type='Maileva SOAP Connector',
  validation_state='validated',
  limit=2)

# Ensure there is no duplication.
if not len(maileva_connector_list):
  raise ValueError('Maileva soap connector is not defined')
elif len(maileva_connector_list) != 1:
  raise ValueError('More them one Maileva soap connector was found!')

return maileva_connector_list[0]
