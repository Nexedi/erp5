portal = context.getPortalObject()

# Do some check here
maileva_connector = portal.portal_catalog.getResultValue(
  reference='maileva_soap_connector',
  validation_state='validated')

if not maileva_connector:
  return context.Base_redirect('view',keep_items={'portal_status_message': 'Maileav soap connector is not defined'})

context.activate().PDF_sendToMailevaByActivity(
  recipient = recipient.getRelativeUrl(),
  sender = sender.getRelativeUrl(),
  connector = maileva_connector.getRelativeUrl()
)
