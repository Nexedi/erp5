portal_type = context.getDeliveryPortalType()
# make sure that the result of the simulation state is update to date, so check getSimulationState manually
return [x.getObject() for x in context.portal_catalog(portal_type=portal_type,simulation_state='planned')
            if x.getObject().getSimulationState()=='planned']
