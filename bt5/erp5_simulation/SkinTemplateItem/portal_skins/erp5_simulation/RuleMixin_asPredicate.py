if context.getTypeInfo() is None:
  # Workaround: unit tests don't always install all the BT that
  # provide the portal types used by 'erp5_simulation_test' BT.
  return context

return context.generatePredicate(criterion_property_list=("start_date",))
