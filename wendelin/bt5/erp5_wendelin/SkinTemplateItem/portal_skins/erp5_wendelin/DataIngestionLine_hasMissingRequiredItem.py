result = False
line = context
aggregate_portal_type_list = [
    x.getPortalType() for x in line.getAggregateValueList()]
if line.getQuantity() > 0:
  resource = line.getResourceValue()
  if resource is not None:
    for portal_type in resource.getRequiredAggregatedPortalTypeList():
      if portal_type not in aggregate_portal_type_list:
        result = True
return result
