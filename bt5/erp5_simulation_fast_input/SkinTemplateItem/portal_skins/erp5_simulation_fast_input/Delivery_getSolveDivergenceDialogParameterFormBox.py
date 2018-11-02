portal = context.getPortalObject()
solver_process = context.getSolverValueList()[-1]
if solver_process.getValidationState() == 'solving':
  return

solver_decision_uid = int(solver_decision_uid)
solver_decision = None
for solver_decision in solver_process.objectValues(portal_type="Solver Decision"):
  if solver_decision.getUid() == solver_decision_uid:
    break
assert solver_decision is not None, \
  "unable to find solver decision with uid : %r on %r" % (
    solver_decision_uid, solver)
solver_value = None
if solver:
  solver_value = portal.restrictedTraverse(solver)
  solver_decision.setSolverValue(solver_value)
else:
  solver_decision.setSolverList([])
  return ''

return solver_decision.SolverDecision_render(context)
