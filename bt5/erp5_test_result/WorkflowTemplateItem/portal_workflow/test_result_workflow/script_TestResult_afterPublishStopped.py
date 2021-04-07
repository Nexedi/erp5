test_result = state_change['object']
if test_result.getPortalType() == "Test Result":
  for line in test_result.objectValues(portal_type="Test Result Line"):
    if line.getSimulationState() == "stopped":
      line.publishStopped()
