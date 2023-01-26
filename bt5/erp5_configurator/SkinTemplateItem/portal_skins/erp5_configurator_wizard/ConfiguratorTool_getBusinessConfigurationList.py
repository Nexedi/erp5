"""
 Returns a list of tuple with max three business configuration for each tuple.
 The business configurations without Resource are just ignored
"""
bc_list = context.business_configuration_module.searchFolder(
                              portal_type="Business Configuration",
                              simulation_state=state,
                              resource_relative_url="portal_workflow/%")

bc_list = [bc.getObject() for bc in bc_list if bc.getResourceValue() is not None]

bc_tuple_list = []
index = 0
while True:
  part = bc_list[index:index+3]
  if not part:
    return bc_tuple_list
  else:
    bc_tuple_list.append(tuple(part))
    index += 3
