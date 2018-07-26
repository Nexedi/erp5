solver_process = context
for solver in solver_process.objectValues(
    portal_type=solver_process.getPortalObject().getPortalTargetSolverTypeList()):
  if solver.getValidationState() != 'solved':
    break
else:
  portal = context.getPortalObject()
  if portal.portal_workflow.isTransitionPossible(solver_process, 'succeed'):
    solver_process.succeed()
