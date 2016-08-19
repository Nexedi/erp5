if REQUEST is not None:
  raise ValueError("This script can't be called in the URL")

result_list = context.getPortalObject().portal_catalog(
  portal_type="Google Connector",
  reference=reference,
  validation_state="validated",
  limit=2,
)

assert result_list, "Google Connector not found"

if len(result_list) == 2:
  raise ValueError("Impossible to select one Google Connector")

google_connector = result_list[0].getObject()
return google_connector.getClientId(), google_connector.getSecretKey()
