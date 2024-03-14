portal = context.getPortalObject()
network_id = context.getSourceSectionValue().getDefaultNetworkIdReference()
return portal.ERP5Site_getCxmlConnectorValue(network_id)
