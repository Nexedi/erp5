total = 0
precision = 2
source_section = context.getSourceSectionValue(portal_type='Organisation')
if source_section is not None:
  precision = context.getQuantityPrecisionFromResource(source_section.getPriceCurrency())

for line in context.objectValues(
      portal_type = context.getPortalAccountingMovementTypeList()):
  total += round(line.getSourceInventoriatedTotalAssetDebit(), precision)

return total
