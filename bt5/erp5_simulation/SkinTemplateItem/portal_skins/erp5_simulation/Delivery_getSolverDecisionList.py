solver_process = context.Delivery_getSolverProcess()
# XXX should omit 'solved' decision?
return solver_process.SolverProcess_getSolverDecisionList()
