portal = context.getPortalObject()
for connector in portal.portal_catalog(
      portal_type="Caucase Connector",
      # We limit this alarm to update the only the connector
      # related to Certificate Login
      reference="erp5-certificate-login",
      validation_state="validated"
    ):
  connector.updateCACertificateChain()
