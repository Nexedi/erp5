parent = context.getParentValue()
if parent.getPortalType() == 'Applied Rule':
  parent_rule = parent.getSpecialiseValue()
  if parent_rule.getReference() == 'order_simulation_rule_for_simulation_fast_input_test':
    return True
return False
