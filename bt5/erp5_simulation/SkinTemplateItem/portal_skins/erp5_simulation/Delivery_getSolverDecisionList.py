solver_process = context.Delivery_getSolverProcess()
if solver_process is None:
  return []

# XXX should omit 'solved' decision?
return solver_process.SolverProcess_getSolverDecisionList()
