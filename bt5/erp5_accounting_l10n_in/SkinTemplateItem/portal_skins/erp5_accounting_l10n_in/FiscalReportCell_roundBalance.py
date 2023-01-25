""" round according to (french) fiscality rules """
amount=float(amount or 0)
fractionalPart, integerPart = math.modf(amount)
if math.fabs(fractionalPart) > 0.49999 :
  if integerPart > 0 :
    integerPart += 1
  elif integerPart < 0:
    integerPart -= 1
return int(integerPart)
