portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

catalog_id_list = []
connection_id_list = []
deferred_connection_id_list = []

for i in range(164, 200):
  catalog_id = 'erp5_mysql_innodb%s'%i
  catalog_id_list.append(catalog_id)
  connection_id = 'erp5_sql_connection%s'%i
  connection_id_list.append(connection_id)
  deferred_connection_id = 'erp5_sql_deferred_connection%s'%i
  deferred_connection_id_list.append(deferred_connection_id)

portal.manage_delObjects(connection_id_list)
portal.manage_delObjects(deferred_connection_id_list)
portal_catalog.manage_delObjects(catalog_id_list)
