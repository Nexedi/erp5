modified = state_change['object']

manager = modified.getParentValue()
if manager.getPortalType() == 'Business Manager':
  # Explicilty update the building_state of Business Manager
  manager.changeBuildingStatetoModified()
