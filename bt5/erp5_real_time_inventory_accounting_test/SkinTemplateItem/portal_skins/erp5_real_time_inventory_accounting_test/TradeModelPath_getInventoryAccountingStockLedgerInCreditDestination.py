delivery_portal_type = movement.getDeliveryValue().getPortalType()
assert delivery_portal_type # XXX debug
if delivery_portal_type.startswith('Purchase Packing List'):
  if movement.getDestination() == 'organisation_module/supplier':
    return ['source/account_module/stock_parts_port']
elif delivery_portal_type.startswith('Internal Packing List'):
  if movement.getDestination() == 'organisation_module/park':
    return ['source/account_module/stock_car_park']
else:
  raise NotImplementedError

return []
