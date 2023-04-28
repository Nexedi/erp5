delivery = state_change['object']

portal = delivery.getPortalObject()
if not (hasattr(portal, 'portal_solvers') and hasattr(portal, 'portal_solver_processes')):
  delivery.diverge()
else:
  solver_tag = '%s_solve' % delivery.getPath()
  delivery.activate(activity='SQLDict', tag=solver_tag).Delivery_solveDivergenceAutomatically()
