movement = context

parent = movement.getParentValue()
if parent.getPortalType() == 'Applied Rule':
  parent_rule = parent.getSpecialiseValue()
  parent_rule_portal_type = parent_rule.getPortalType()
  if parent_rule_portal_type not in ['Delivery Root Simulation Rule', 'Delivery Simulation Rule']:
    return False
  # XXX can we create invoicing rule for Production Order?
  if parent_rule_portal_type in ['Delivery Simulation Rule',] and \
      parent.getParentValue().getParentValue().getSpecialiseValue().getPortalType() not in ['Order Root Simulation Rule']:
    return False

  
# 
# Some business process does not generate invoice.
# XXX isn't there a better way to configure this ???

if 'business_process_module/4/delivery_path' in movement.getCausalityList():
  return False

source_section = movement.getSourceSection()
destination_section = movement.getDestinationSection()
if source_section == destination_section or source_section is None \
    or destination_section is None:
  return False

return True
