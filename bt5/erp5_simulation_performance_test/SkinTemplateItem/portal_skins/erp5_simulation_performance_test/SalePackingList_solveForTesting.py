portal = context.getPortalObject()
solver_process = portal.portal_solver_processes.newSolverProcess(context)
solver_decision, = [x for x in solver_process.objectValues()
  if x.getCausalityValue().getTestedProperty() == property]
solver_decision.setSolverValue(portal.portal_solvers['Unify Solver'])
solver_decision.updateConfiguration(tested_property_list=[property], value=value)
solver_process.buildTargetSolverList()
solver_process.solve()
