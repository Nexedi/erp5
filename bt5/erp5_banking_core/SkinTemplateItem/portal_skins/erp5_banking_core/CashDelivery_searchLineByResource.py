for line in context.objectValues(portal_type=portal_type):
  if line.getResourceId() == resource_id:
    return line
return None
