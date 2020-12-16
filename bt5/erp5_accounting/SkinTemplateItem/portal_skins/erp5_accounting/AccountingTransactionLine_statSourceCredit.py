total = 0
precision = context.getQuantityPrecisionFromResource(context.getResource())
for line in context.objectValues(
    portal_type=context.getPortalAccountingMovementTypeList()):
  total += round(line.getSourceCredit(), precision)

return total
