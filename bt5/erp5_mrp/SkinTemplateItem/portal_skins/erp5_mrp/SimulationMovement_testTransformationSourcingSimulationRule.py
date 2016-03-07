rule = context.getParentValue().getSpecialiseValue()
return rule.getPortalType() == "Transformation Simulation Rule" \
   and rule.testTransformationSourcing(context)
