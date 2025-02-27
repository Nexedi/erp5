component = state_change['object']
component.getPortalObject().portal_components.resetOnceAtTransactionBoundary(
  only_test_component_module=component.getPortalType() == 'Test Component'
)
