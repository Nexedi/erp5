obj = state_change['object']

# User explicitely wants to validate again (example use case: import-error
# on ZODB Components which have now been fixed)
if obj.getValidationState() == 'modified':
  obj.checkSourceCode()

obj.Base_checkConsistency()
