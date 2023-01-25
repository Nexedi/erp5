from DateTime import DateTime
now = DateTime()
#Clean-up invalidated Test Nodes and
# invalidate inactive ones
list_node = context.portal_catalog(
       portal_type="Test Node",
       )
default_old_date = now-1.0/24*11
for test_node in list_node:
  old_date = default_old_date
  test_node = test_node.getObject()
  ping_date = test_node.getPingDate()
  validation_state = test_node.getValidationState()
  distributor = test_node.getSpecialiseValue()
  if distributor is not None:
    timeout_method = getattr(distributor, 'getProcessTimeout', None)
    if timeout_method is not None:
      timeout = timeout_method()
      if timeout:
        old_date = now - float(timeout)/(24*3600)
  if validation_state == 'validated':
    if ping_date is not None:
      if ping_date <= old_date:
        test_node.invalidate()
  elif validation_state == 'invalidated':
    __traceback_info__ = test_node # pylint:disable=unused-variable
    if test_node.getSpecialise():
      test_node.getSpecialiseValue().cleanupInvalidatedTestNode(test_node)

portal = context.getPortalObject()

distributor_list = portal.portal_task_distribution.objectValues()
for distributor in distributor_list:
  distributor.activate(tag=tag).optimizeConfiguration()

context.activate(after_tag=tag).getId()
return list_node
