debit_price = getattr(brain, 'debit_price', None)
if debit_price is None:
  if brain.isCancellationAmount():
    debit_price = min(brain.total_price, 0)
  else:
    debit_price = max(brain.total_price, 0)
return debit_price
