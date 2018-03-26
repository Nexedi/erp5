result = sorted([
  x for x in context.getAggregateValueList(portal_type='Internet Message Post')
  if x.getSimulationState() in ('exported', 'acknowledged')
], key=lambda x:x.getCreationDate())

if len(result):
  return result[-1]
else:
  return None
