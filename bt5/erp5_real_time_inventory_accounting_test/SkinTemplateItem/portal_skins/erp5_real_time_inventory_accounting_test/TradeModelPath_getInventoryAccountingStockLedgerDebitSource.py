use = movement.getUse()
if use == 'trade/sale':
  if movement.getSource() == 'organisation_module/hoge':
    return ['source/account_module/stock_car_park']
elif use == 'trade/purchase':
  return []
else:
  raise NotImplementedError

return []
