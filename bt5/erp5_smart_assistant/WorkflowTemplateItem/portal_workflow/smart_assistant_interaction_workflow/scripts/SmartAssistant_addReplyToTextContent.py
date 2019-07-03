document = state_change['object']
if document.getValidationState() in ("draft","responded"):
  document.submit()
