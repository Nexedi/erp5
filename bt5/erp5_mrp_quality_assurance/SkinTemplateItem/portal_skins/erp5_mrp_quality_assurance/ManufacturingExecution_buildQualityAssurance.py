if context.getSimulationState() != 'confirmed':
  return
production_order = context.getCausalityValue(portal_type='Production Order')
ME_execution = None
for me in production_order.getCausalityRelatedValueList(portal_type='Manufacturing Execution'):
  if me.getLedger() == 'manufacturing/execution':
    ME_execution = me
    break
if ME_execution is None:
  return
context.fixConsistency()
context.setReady()
