movement = context

parent = movement.getParentValue()
if parent.getPortalType() == 'Applied Rule':
  parent_rule = parent.getSpecialiseValue()
  if parent_rule.getPortalType() not in ['Order Root Simulation Rule', 'Production Order Root Simulation Rule']:
    return False

return True
