"""
This script returns a dictionary of default properties for Unify Solver.

This is a sample implementation that returns the first item in each list.
"""
value_list_dict = context.UnifySolver_getConfigurationPropertyListDict()
value_dict = {}
for property_id, value_list in list(value_list_dict.items()):
  value_dict[property_id] = value_list[0]
return value_dict
