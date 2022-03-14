decision = state_change['object']

# Get parent object
parent_decision = decision.getParentValue()

# Set it to decide if decision was forwarded
# Must be improved to count number of subdecisions and support multiple forward
if parent_decision.getValidationState() == 'forwarded':
  parent_decision.decide()
