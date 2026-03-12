portal_components = context.getPortalObject().portal_components
for component_id in portal_components.objectIds():
  print component_id
return printed
