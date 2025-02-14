if context.getPortalType() != 'Manufacturing Execution':
  raise ValueError(' %s type error' % context.getRelativeUrl())
if context.getSimulationState() in ('started', 'stopped'):
  for line in context.objectValues(portal_type='Manufacturing Execution Line'):
    if line.getIntIndex() == -1:
      line.fixConsistency()
      quality_control = line.getAggregateValue(portal_type='Quality Control')
      if quality_control.getValidationState() == 'queued':
        quality_control.confirm()
