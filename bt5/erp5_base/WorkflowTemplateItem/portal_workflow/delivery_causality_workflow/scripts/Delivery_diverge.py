delivery = state_change['object']
draft_solver_process = None
for solver_process in delivery.getSolverValueList():
  validation_state = solver_process.getValidationState()
  if validation_state == 'solving':
    # Currently solving Divergences through solve() Activity
    return
  elif solver_process.getValidationState() == 'draft':
    draft_solver_process = solver_process

if draft_solver_process is not None:
  draft_solver_process.buildSolverDecisionList(delivery)
else:
  delivery.getPortalObject().portal_solver_processes.newSolverProcess(delivery)
