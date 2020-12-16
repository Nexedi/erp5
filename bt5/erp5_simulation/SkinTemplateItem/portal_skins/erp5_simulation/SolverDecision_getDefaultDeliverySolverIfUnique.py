# type: () -> Optional[str]
"""Returns the id of delivery solver if there's only one configured
on this solver, None otherwise.
"""
delivery_solver_list = context.searchDeliverySolverList()
if len(delivery_solver_list) == 1:
  return delivery_solver_list[0].getId()
