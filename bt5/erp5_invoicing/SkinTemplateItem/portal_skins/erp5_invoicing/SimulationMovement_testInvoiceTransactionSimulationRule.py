movement = context

parent = movement.getParentValue()
if parent.getPortalType() != 'Applied Rule':
  return False

parent_rule = parent.getSpecialiseValue()
if parent_rule.getPortalType() not in ('Invoice Root Simulation Rule',
                                       'Invoice Simulation Rule',
                                       'Trade Model Simulation Rule',
                                       'Pay Sheet Root Simulation Rule'):
  return False

delivery_movement = movement.getDeliveryValue()
if delivery_movement is not None and (
   delivery_movement.getPortalType() not in movement.getPortalInvoiceMovementTypeList()
    and delivery_movement.getPortalType() not in movement.getPortalTaxMovementTypeList()):
  return False

return True
