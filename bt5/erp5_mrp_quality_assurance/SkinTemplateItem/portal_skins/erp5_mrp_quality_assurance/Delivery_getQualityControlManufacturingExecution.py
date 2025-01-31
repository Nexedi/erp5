for me in context.getCausalityValue(portal_type='Production Order').getCausalityRelatedValueList(portal_type='Manufacturing Execution'):
  if me.getLedger() == "manufacturing/quality_insurance":
    return me
raise ValueError('Could not find quality control for %s' % context.getRelativeUrl())
