from Products.ZSQLCatalog.SQLCatalog import Query
from DateTime import DateTime
now = DateTime()
#Clean-up invalidated Test Nodes and
# invalidate inactive ones 
list_node = context.portal_catalog(
       portal_type="Test Node",
       )
old_date = now-1.0/24*11
for test_node in list_node:
  test_node = test_node.getObject()
  ping_date = test_node.getPingDate()
  validation_state = test_node.getValidationState()
  if validation_state == 'validated':
    if ping_date is not None:
      if ping_date <= old_date:
        test_node.invalidate()
  elif validation_state == 'invalidated':
    if test_node.getSpecialise():
      test_node.getSpecialiseValue().cleanupInvalidatedTestNode(test_node)

portal = context.getPortalObject()

distributor_list = portal.portal_task_distribution.objectValues()
for distributor in distributor_list: 
  distributor.activate().optimizeConfiguration()
return list_node
