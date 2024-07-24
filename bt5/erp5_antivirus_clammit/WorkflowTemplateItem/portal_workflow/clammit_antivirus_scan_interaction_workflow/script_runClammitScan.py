object_value = state_change['object']
clammit_connector = context.getPortalObject().portal_web_services.searchFolder(
  portal_type="Clammit Connector",
  limit=1,
)
if not clammit_connector:
  raise ValueError("A Clammit Connector must be configured in order to run antivirus scans")
else:
  clammit_connector_value = clammit_connector[0].getObject()
if clammit_connector_value.isSafe(object_value.getData()):
  object_value.setSafe()
else:
  object_value.setInfected()
