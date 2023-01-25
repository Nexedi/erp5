"""
Retrieve the reference corresponding to given client_id.
Because the client_id is not portable between instances, but the reference can be.
"""
# Proxy roles: Auditor to have access to the connector and its client declaration
# Note: Very few rows are expected (0 or 1)
for authorisation_server_row in context.getPortalObject().portal_catalog(
  portal_type='OAuth2 Authorisation Server Connector',
  validation_state='validated',
):
  authorisation_server_value = authorisation_server_row.getObject()
  try:
    client_value = authorisation_server_value[client_id]
  except KeyError:
    continue
  else:
    # Note: client_ids should be globally unique, so it should be highly unlikely for both
    # - multiple server connectors being present
    # - and having client declarations with the same id
    # so do not bother continuing to iterate.
    return client_value.getReference()
