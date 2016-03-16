credit_price = getattr(brain, 'credit_price', None)
if credit_price is None:
  if brain.isCancellationAmount():
    credit_price = min(-(brain.total_price or 0), 0)
  else:
    credit_price = max(-(brain.total_price or 0), 0)
return credit_price
