delivery = context
solver_process_tool = delivery.getPortalObject().portal_solver_processes
# XXX We sometimes want to store solver process document persistently.
solver_process = solver_process_tool.newSolverProcess(delivery, temp_object=True)
if solver_process is not None:
  solver_process.buildTargetSolverList()
  solver_tag = '%s_solve' % delivery.getPath()
  solver_process.solve(activate_kw={'tag':solver_tag})
  delivery.activate(after_tag=solver_tag).updateCausalityState(solve_automatically=False)
else:
  delivery.updateCausalityState(solve_automatically=False)
