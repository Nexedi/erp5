# ERP5 Site is set by erp5_site_global_id
# but fallback to erp5_sql_connection.connection_string for old sites
portal = context.getPortalObject()
erp5_site_global_id = getattr(portal, 'erp5_site_global_id', None)

if erp5_site_global_id is None:
  erp5_site_global_id = portal.erp5_sql_connection.connection_string.split("@")[0]

return erp5_site_global_id
