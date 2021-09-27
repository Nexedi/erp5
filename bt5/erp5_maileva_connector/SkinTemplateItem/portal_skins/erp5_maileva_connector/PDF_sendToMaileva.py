from DateTime import DateTime

now = DateTime()
portal = context.getPortalObject()

# Do some check here
maileva_connector = context.MailevaSOAPConnector_getAvailableConnector()

today = now.toZone('UTC').asdatetime().strftime('%Y-%m-%d')
number = str(portal.portal_ids.generateNewId(
                     id_group='maileva_%s' % today,
                     id_generator='uid')).zfill(6)
reference="maileva-%s-%s" % (today, number)


maileva_connector.activate().submitRequest(
  recipient_url = recipient.getRelativeUrl(),
  sender_url = sender.getRelativeUrl(),
  document_url = context.getRelativeUrl(),
  track_id = reference
)

context.send()
