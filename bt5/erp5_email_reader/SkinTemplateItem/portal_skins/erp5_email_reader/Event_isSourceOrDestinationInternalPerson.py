for o in context.getSourceValueList(portal_type='Person'):
  if o.getRole() == 'internal':
    return True

for o in context.getDestinationValueList(portal_type='Person'):
  if o.getRole() == 'internal':
    return True

return False
