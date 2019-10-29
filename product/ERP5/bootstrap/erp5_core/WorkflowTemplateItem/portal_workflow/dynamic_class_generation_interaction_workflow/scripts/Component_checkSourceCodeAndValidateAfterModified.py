obj = state_change['object']
obj.checkSourceCode()
if not obj.getTextContentErrorMessageList() and obj.getValidationState() == 'modified':
  obj.checkConsistencyAndValidate()
