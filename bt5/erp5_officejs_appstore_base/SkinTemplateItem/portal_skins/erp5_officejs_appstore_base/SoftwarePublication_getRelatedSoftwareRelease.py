for line in context.objectValues(portal_type="Software Publication Line"):
  software_release = line.getAggregateValue(portal_type="Software Release")
  if software_release:
    return software_release

return None
