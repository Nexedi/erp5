from DateTime import DateTime
now = DateTime()
# Consider that a test running for more than 3 hours is a stuck
# test. Very long tests are not good, they should be splitted to
# let testnodes work on other test suites. So if we have 3 hours
# it should mean testnode is dead, this test should be restarted
old_date = now-1.0/24*3
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
