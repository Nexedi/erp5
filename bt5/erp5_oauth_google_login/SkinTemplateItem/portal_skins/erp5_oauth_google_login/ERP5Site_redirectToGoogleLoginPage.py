portal = context.getPortalObject()

google_connector = portal.ERP5Site_getDefaultGoogleConnector()
return google_connector.redirectToGoogleLoginPage(
  "{0}/ERP5Site_receiveGoogleCallback".format(portal.absolute_url()),
  RESPONSE=RESPONSE,
)
