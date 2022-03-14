modified = state_change['object']

scope = modified.getParentValue()
if scope.getPortalType() == "Quantity Unit Conversion Group":
  scope = scope.getParentValue()

if scope.getPortalType() != "Product":
  # This was a global definition.
  # Its change implies that all local definitions need reindexation
  # Even resources that do NOT override definitions need indexation.
  context.QuantityUnitConversionModule_invalidateUniversalDefinitionDict()
  context.product_module.recursiveReindexObject()
else:
  scope.reindexObject()
