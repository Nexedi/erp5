portal_type = context.getDeliveryPortalType()
# make sure that the result of the simulation state is update to date, so check getSimulationState manually
result = []
append = result.append
for x in context.portal_catalog(portal_type=portal_type, simulation_state='confirmed'):
  try:
    x = x.getObject()
  except KeyError:
    # this transaction started before the transaction which created an object is committed.
    continue
  if x.getSimulationState() == 'confirmed':
    append(x)
return result
