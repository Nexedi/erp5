portal = context.getPortalObject()

for i in range(101, 164):
  connection_id = 'erp5_sql_connection%s'%i
  deferred_connection_id = 'erp5_sql_deferred_connection%s'%i
  connection_string = connection_string = 'erp5_test_%(i)s@10.0.159.93:2099 testuser_%(i)s testpassword%(i)s'%{'i': i}
  getattr(portal, connection_id).connect(connection_string)
  getattr(portal, deferred_connection_id).connect(connection_string)
