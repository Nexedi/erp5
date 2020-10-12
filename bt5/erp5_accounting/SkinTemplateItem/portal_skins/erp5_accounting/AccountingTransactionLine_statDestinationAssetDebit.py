total = 0
precision = 2
destination_section = context.getDestinationSectionValue(portal_type='Organisation')
if destination_section is not None:
  precision = context.getQuantityPrecisionFromResource(destination_section.getPriceCurrency())

for line in context.objectValues(
        portal_type=context.getPortalAccountingMovementTypeList()):
  total += round(line.getDestinationInventoriatedTotalAssetDebit(), precision)

return total
