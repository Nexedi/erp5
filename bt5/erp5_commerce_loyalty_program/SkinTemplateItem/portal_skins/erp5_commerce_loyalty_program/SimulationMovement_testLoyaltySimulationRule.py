movement = context

parent = movement.getParentValue()
if parent.getPortalType() == 'Applied Rule':
  parent_rule = parent.getSpecialiseValue()
  parent_rule_portal_type = parent_rule.getPortalType()
  if parent_rule_portal_type not in ['Delivery Root Simulation Rule', 'Delivery Simulation Rule']:
    return False
  if parent_rule_portal_type in ['Delivery Simulation Rule',] and \
      parent.getParentValue().getParentValue().getSpecialiseValue().getPortalType() not in ['Order Root Simulation Rule']:
    return False

source_section = movement.getSourceSection()
destination_section = movement.getDestinationSection()
if source_section == destination_section or source_section is None \
    or destination_section is None:
  return False
destination_value = movement.getDestinationValue()
if not destination_value or not destination_value.objectValues(portal_type='Loyalty Account'):
  return False

return True
