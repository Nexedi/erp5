# XXX currently we create a Solver Process and build Solver Decision in it if missing.
# But for better performance, Solver Process and Solver Decision should be created beforehand
# by causality workflow when a delivery becomes divergent.
for solver_process in context.getSolverValueList():
  if solver_process.getValidationState() == 'draft':
    solver_process.buildSolverDecisionList(context)
    break
else:
  solver_process = context.getPortalObject().portal_solver_processes.newSolverProcess(context)

return solver_process
