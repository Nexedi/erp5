delivery = state_change['object']

portal = delivery.getPortalObject()
try:
  portal.portal_solvers
  portal.portal_solver_processes
except AttributeError:
  delivery.diverge()
else:
  solver_tag = '%s_solve' % delivery.getPath()
  delivery.activate(tag=solver_tag).Delivery_solveDivergenceAutomatically()
