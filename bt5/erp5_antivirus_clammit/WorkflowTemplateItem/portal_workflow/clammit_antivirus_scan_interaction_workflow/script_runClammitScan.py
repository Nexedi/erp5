from erp5.component.module.Log import log

object_value = state_change['object']
clammit_connector, = context.getPortalObject().portal_web_services.searchFolder(
  portal_type="Clammit Connector",
  limit=1,
)
clammit_connector_value = clammit_connector.getObject()
comment = "Checked by ClamAV Antivirus"
if clammit_connector_value.isSafe(object_value.getData()):
  object_value.setSafe(comment=comment)
else:
  log("ClamAV result: the file %s has been found infected" % object_value.getRelativeUrl())
  object_value.setInfected(comment=comment)
