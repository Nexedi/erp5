#
#  This method is used by the invoice_transaction_builder
# delivery builder to select the Invoice Transaction
# in which creating new Invoice Transaction Lines.
#

deliveries_keys = {}
for movement in movement_list:
  ar = movement.getParentValue()
  line = None

  # case of trade model movement
  if ar.getParentValue().getParentValue().getSpecialiseValue().getPortalType() == 'Trade Model Simulation Rule':
    line = ar.getParentValue().getParentValue().getParentValue().getDeliveryValue()

  # in case of invoice rule (ie. starting from Invoice)
  if line is None:
    line = ar.getParentValue().getOrderValue()

  # in case of invoicing rule (ie. starting from Order)
  if line is None:
    line = movement.getParentValue().getParentValue().getDeliveryValue()

  if line is not None:
    deliveries_keys[line.getExplanationValue()] = 1

return [x for x in deliveries_keys.keys() if x is not None]
