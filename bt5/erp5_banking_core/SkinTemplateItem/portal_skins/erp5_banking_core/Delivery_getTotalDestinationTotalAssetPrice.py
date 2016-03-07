total = 0
for line in context.objectValues(portal_type=portal_type):
  if line.getDestinationTotalAssetPrice() is not None:
     total += line.getDestinationTotalAssetPrice()
return total
