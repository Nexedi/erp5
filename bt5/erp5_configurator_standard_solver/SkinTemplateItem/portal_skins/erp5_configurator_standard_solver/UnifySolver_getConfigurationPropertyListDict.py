"""
This script returns a dictionary of possible values for Unify Solver.
"""
solver_decision = context.getCausalityValue()
tester = solver_decision.getCausalityValue()
value_list_dict = {}
for property_id in tester.getTestedPropertyList():
  value_list = []
  for simulation_movement in context.getDeliveryValueList():
    movement = simulation_movement.getDeliveryValue()
    value = movement.getProperty(property_id)
    if value not in value_list:
      value_list.append(value)
    value = simulation_movement.getProperty(property_id)
    if value not in value_list:
      value_list.append(value)
  value_list_dict[property_id] = [(x, str(x)) for x in value_list]
return value_list_dict
