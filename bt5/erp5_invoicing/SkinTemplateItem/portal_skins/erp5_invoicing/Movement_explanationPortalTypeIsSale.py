explanation_value = context.getExplanationValue()
if explanation_value is not None:
  if explanation_value.getPortalType().startswith('Sale'):
    return 1
return 0
