ME = context.getCausalityValue(portal_type='Manufacturing Execution')

if ME:
  return ME.ManufacturingExecution_getPastedQualityHistory(**kw)
return []
