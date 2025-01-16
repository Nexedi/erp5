ME = context.getCausalityValue(portal_type='Manufacturing Execution')
if ME:
  return ME.Delivery_getVINRelatedDefectList(**kw)
return []
