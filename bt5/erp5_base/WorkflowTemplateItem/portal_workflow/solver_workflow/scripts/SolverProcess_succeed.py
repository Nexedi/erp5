solver_process = state_change['object'].getParentValue()
for solver in solver_process.objectValues(
    portal_type=solver_process.getPortalObject().getPortalTargetSolverTypeList()):
  if solver.getValidationState() != 'solved':
    return
solver_process.succeed()
