parent = context.getParentValue()
if parent.getPortalType() != 'Applied Rule':
  return False

if not context.hasPrice():
  return False

parent_rule = parent.getSpecialiseValue()
if parent_rule.getPortalType() not in ('Delivery Root Simulation Rule',
                                       'Delivery Simulation Rule'):
  return False

return True
