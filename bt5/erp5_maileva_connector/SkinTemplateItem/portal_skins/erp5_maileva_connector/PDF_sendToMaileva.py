portal = context.getPortalObject()

# Do some check here
maileva_connector = portal.portal_catalog.getResultValue(
  reference='maileva_soap_connector',
  validation_state='validated')


if not maileva_connector:
  raise ValueError('Maileav soap connector is not defined')

context.activate().PDF_sendToMailevaByActivity(
  recipient = recipient.getRelativeUrl(),
  sender = sender.getRelativeUrl(),
  connector = maileva_connector.getRelativeUrl()
)

context.send()
