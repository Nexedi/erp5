modified = state_change['object']

grand_parent = modified.getParentValue().getParentValue()

activate_kw=dict(after_path=modified.getPath())

if grand_parent.getPortalType() == "Product":
  # If measure is local
  grand_parent.reindexObject(activate_kw=activate_kw)
else:
  # This was a global definition.
  # Its change implies that all local definitions need reindexation
  # Even resources that do NOT override definitions need indexation.
  context.activate(tag="QuantityUnitConversionDefinition_reindexResource", **activate_kw).QuantityUnitConversionModule_invalidateUniversalDefinitionDict()
  activate_kw["after_tag"] = "QuantityUnitConversionDefinition_reindexResource"
  context.product_module.recursiveReindexObject(activate_kw=activate_kw)
