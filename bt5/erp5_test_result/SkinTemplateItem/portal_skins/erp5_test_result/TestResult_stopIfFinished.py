"""
Check if a test result is finished and move test result to stopped if this is the case
"""
test_result = context
if test_result.getSimulationState() == "started":
  if {"stopped"} == {x.getSimulationState()
      for x in test_result.objectValues(portal_type="Test Result Line")}:
    test_result.stop()
