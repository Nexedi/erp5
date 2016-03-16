obj = state_change['object']
if obj.getValidationState() == 'validated':
  obj.modify()
