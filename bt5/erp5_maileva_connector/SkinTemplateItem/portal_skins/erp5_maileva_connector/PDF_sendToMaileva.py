from DateTime import DateTime

now = DateTime()
portal = context.getPortalObject()

# Do some check here
maileva_connector = portal.ERP5Site_getAvailableMailevaSOAPConnector()

today = now.toZone('UTC').asdatetime().strftime('%Y-%m-%d')
number = str(portal.portal_ids.generateNewId(
                     id_group='maileva_%s' % today,
                     id_generator='uid')).zfill(6)
reference="maileva-%s-%s" % (today, number)

xml = maileva_connector.generateRequestXML(
  recipient = recipient,
  sender =sender,
  document=context,
  track_id=reference
)

maileva_exchange = context.system_event_module.newContent(
  portal_type='Maileva Exchange',
  source_value = sender,
  destination_value = recipient,
  resource_value = maileva_connector,
  follow_up_value = context,
  reference=reference,
  request = xml
)

maileva_exchange.activate().MailevaExchange_submitMailevaRequest()

context.send()
