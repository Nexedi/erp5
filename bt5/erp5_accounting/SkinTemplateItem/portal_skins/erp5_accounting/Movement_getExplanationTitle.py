movement = brain.getObject()
if movement.hasTitle():
  return movement.getTitle()
return movement.getExplanationValue().getTitle()
