"""
  Get all states and descriptions to present at the
  the form.
"""

result = []
previous_state_list = []
workflow = business_configuration.getResourceValue()
state = workflow.getSourceValue()

while state not in previous_state_list:
  transition = state.getDestinationValue()
  previous_state_list.append(state)
  if transition is None:
    break

  state = transition.getDestinationValue()
  if state is None:
    break

  if transition.getTransitionFormId() not in (None, ""):
    result.append({'state' : state.getTitle(),
                    'description' : state.getDescription(),
                    'title': state.getTitle()})

return result
