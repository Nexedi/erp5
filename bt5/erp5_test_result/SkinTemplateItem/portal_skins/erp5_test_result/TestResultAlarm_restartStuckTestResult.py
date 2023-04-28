"""
Look for all ongoing tests and check if some lines are in
state "started" since too long. If so, this surely means that
the testnode is dead (like machine was turned off). If so,
we should set back test line in state "draft" so that another
testnode will do the job.
"""
portal = context.getPortalObject()
for test_result in portal.portal_catalog(portal_type="Test Result",
                                         simulation_state="started"):
  test_result.getObject().activate(activity='SQLDict', priority=5).TestResult_restartStuckLine()
