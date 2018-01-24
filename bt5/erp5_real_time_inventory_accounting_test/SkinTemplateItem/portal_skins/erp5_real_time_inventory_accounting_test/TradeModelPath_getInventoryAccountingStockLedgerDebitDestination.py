use = movement.getUse()
if use == 'trade/sale':
  return []
elif use == 'trade/purchase':
  if movement.getDestination() == 'organisation_module/supplier':
    return ['source/account_module/variation_parts']
else:
  raise NotImplementedError

return []
