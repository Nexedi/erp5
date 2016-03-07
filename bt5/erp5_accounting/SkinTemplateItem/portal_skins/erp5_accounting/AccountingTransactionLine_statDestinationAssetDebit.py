total = 0
for line in context.objectValues(
          portal_type = context.getPortalAccountingMovementTypeList()) :
  total += line.getDestinationInventoriatedTotalAssetDebit()
  
return total
