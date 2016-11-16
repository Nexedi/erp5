portal = context.getPortalObject()
original_connection_id = 'test_connection'
original_deferred_connection_id = 'erp5_sql_deferred_connection'

for i in range(164, 165):
  new_connection_id = 'erp5_sql_connection%s'%str(i)
  new_deferred_connection_id = 'erp5_sql_deferred_connection%s'%i
  new_connection_string = 'erp5_test_%(i)s@10.0.159.93:2099 testuser_%(i)s testpassword%(i)s'%{'i': i}

  # Skip this test if default connection string is not "test test".
  original_connection = getattr(portal, original_connection_id)
  connection_string = original_connection.connection_string
  if (connection_string == new_connection_string):
    message = 'SKIPPED: default connection string is the same as the default catalog'
    ZopeTestCase._print(message)
    LOG('Testing... ',0,message)

  addSQLConnection = portal.manage_addProduct['ZMySQLDA'] \
    .manage_addZMySQLConnection
  # Create new connectors
  try:
    addSQLConnection(new_connection_id,'', new_connection_string)
    new_connection = portal[new_connection_id]
    new_connection.manage_open_connection()
    addSQLConnection(new_deferred_connection_id,'', new_connection_string)
    new_connection = portal[new_deferred_connection_id]
    new_connection.manage_open_connection()
  except:
    pass
  # the transactionless connector must not be changed because this one
  # creates the portal_ids otherwise it will create conflicts with uid
  # objects

  # Create new catalog
  portal_catalog = portal.portal_catalog
  erp5_catalog = portal_catalog.getSQLCatalog()
  original_catalog_id = 'erp5_mysql_innodb'
  new_catalog_id = original_catalog_id + str(i)
  new_catalog = portal_catalog.cloneCatalog(new_catalog_id)
  #new_catalog = portal_catalog.manage_clone(erp5_catalog, new_catalog_id)
  #self.tic()
  # Parse all methods in the new catalog in order to change the connector
  source_sql_connection_id_list=list((original_connection_id,
                                original_deferred_connection_id))
  destination_sql_connection_id_list=list((new_connection_id,
                                     new_deferred_connection_id))

  # Construct a mapping for connection ids.
  sql_connection_id_dict = None
  if source_sql_connection_id_list is not None and \
     destination_sql_connection_id_list is not None:
    sql_connection_id_dict = {}
    for source_sql_connection_id, destination_sql_connection_id in \
        zip(source_sql_connection_id_list,
            destination_sql_connection_id_list):
      if source_sql_connection_id != destination_sql_connection_id:
        sql_connection_id_dict[source_sql_connection_id] = \
            destination_sql_connection_id

  # Call the method to update the connection ids for the new catalog
  portal_catalog.changeSQLConnectionIds(new_catalog,
                              sql_connection_id_dict)
  # Clear the new catalog incase it uses some old connection string
  new_catalog.manage_catalogClear()
  # Now validate the newly created catalog
  #new_catalog.validate()
