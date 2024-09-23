from erp5.component.module.Log import log

# Raise if this script is not called within an activity
context.getActivityRuntimeEnvironment()

clammit_connector, = context.getPortalObject().portal_web_services.searchFolder(
  portal_type="Clammit Connector",
  limit=1,
)
clammit_connector_value = clammit_connector.getObject()
comment = "Checked by ClamAV Antivirus"
if clammit_connector_value.isSafe(context.getData()):
  context.setSafe(comment=comment)
else:
  log("ClamAV result: the file %s has been found infected" % context.getRelativeUrl())
  context.setInfected(comment=comment)
