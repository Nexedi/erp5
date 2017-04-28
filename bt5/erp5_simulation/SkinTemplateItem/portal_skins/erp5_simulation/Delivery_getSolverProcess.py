for solver_process in context.getSolverValueList():
  if solver_process.getValidationState() == 'draft':
    return solver_process
