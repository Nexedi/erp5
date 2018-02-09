delivery_portal_type = movement.getDeliveryValue().getPortalType()
assert delivery_portal_type # XXX debug
if delivery_portal_type.startswith('Sale Packing List'):
  if movement.getSource() == 'organisation_module/hoge':
    return ['source/account_module/variation_cars']
elif delivery_portal_type.startswith('Internal Packing List'):
  return ['source/account_module/variation_cars']
else:
  raise NotImplementedError

return []
