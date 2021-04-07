delivery = state_change['object']
delivery_solve_property_dict = state_change['kwargs'].get('delivery_solve_property_dict', {})
divergence_to_accept_list = state_change['kwargs'].get('divergence_to_accept_list', [])
divergence_to_adopt_list = state_change['kwargs'].get('divergence_to_adopt_list', [])

if len(delivery_solve_property_dict) or len(divergence_to_accept_list) \
    or len(divergence_to_adopt_list):
  delivery_relative_url = delivery.getRelativeUrl()
  delivery_builder_list = delivery.getBuilderList()
  if len(delivery_solve_property_dict):
    for delivery_builder in delivery_builder_list:
      delivery_builder.solveDeliveryGroupDivergence(delivery_relative_url,
                                                    property_dict=delivery_solve_property_dict)
  for delivery_builder in delivery_builder_list:
    delivery_builder.solveDivergence(delivery_relative_url,
                                     divergence_to_accept_list=divergence_to_accept_list,
                                     divergence_to_adopt_list=divergence_to_adopt_list)
