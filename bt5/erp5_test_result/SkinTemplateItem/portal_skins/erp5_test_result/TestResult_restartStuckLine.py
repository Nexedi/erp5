from DateTime import DateTime
now = DateTime()

timeout = None
# Try to fetch timeout from distributor if defined there...
for test_result_node in context.contentValues(portal_type='Test Result Node'):
  test_node = test_result_node.getSpecialiseValue(portal_type='Test Node')
  if test_node is not None:
    distributor = test_node.getSpecialiseValue(portal_type='ERP5 Project Unit Test Distributor')
    if distributor is not None:
      if distributor.getProcessTimeout() is not None:
        timeout = distributor.getProcessTimeout()
        break

# ...or fallback to default:
# Consider that a test running for more than 3 hours is a stuck
# test. Very long tests are not good, they should be splitted to
# let testnodes work on other test suites. So if we have 3 hours
# it should mean testnode is dead, this test should be restarted
if timeout is None:
  timeout = 1.0/24*3
else:
  # transform it has number of days (instead of seconds)
  timeout = float(timeout) / 3600 / 24

old_date = now-timeout
if context.getSimulationState() == "started":
  for line in context.objectValues(portal_type="Test Result Line"):
    if line.getSimulationState() == "started":
      history_list = line.Base_getWorkflowHistoryItemList('test_result_workflow', display=0)
      history_list.reverse()
      for history in history_list:
        if history.action == 'start':
          if history.time < old_date:
            line.redraft()
            assert line.getSimulationState() == "draft"
          break
