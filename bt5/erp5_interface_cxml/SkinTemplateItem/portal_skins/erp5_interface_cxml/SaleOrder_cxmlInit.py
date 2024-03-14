for line in context.objectValues(portal_type="Sale Order Line"):
  if context.getStopDate() != line.getStopDate():
    context.setStopDate(line.getStopDate())
  if context.getStartDate() != line.getStartDate():
    context.setStartDate(line.getStartDate())
  break
