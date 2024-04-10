portal = context.getPortalObject()
result_list = portal.portal_catalog(
  portal_type="Google Connector",
  reference=reference,
  validation_state="validated",
  limit=2)
if len(result_list) != 1:
  raise ValueError("Impossible to select one Google Connector")
return result_list[0].getObject()
