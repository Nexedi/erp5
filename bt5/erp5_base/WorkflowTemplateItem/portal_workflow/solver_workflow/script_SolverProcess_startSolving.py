solver_process = state_change['object'].getParentValue()
if solver_process.getValidationState() == 'draft':
  solver_process.startSolving()
