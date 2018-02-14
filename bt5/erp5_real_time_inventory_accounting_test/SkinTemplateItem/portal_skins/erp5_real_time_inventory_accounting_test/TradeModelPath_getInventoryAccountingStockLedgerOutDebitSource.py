delivery_portal_type = movement.getDeliveryValue().getPortalType()
assert delivery_portal_type # XXX debug
if delivery_portal_type.startswith('Sale Packing List'):
  if movement.getSource() == 'organisation_module/hoge':
    return ['source/account_module/stock_car_park']
elif delivery_portal_type.startswith('Internal Packing List') or delivery_portal_type.startswith('Production Packing List'):
  if movement.getSource() == 'organisation_module/workshop':
    return ['source/account_module/stock_car_workshop']
else:
  raise NotImplementedError

return []
