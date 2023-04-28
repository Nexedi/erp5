tag = script.id
for exchange in context.getPortalObject().system_event_module.searchFolder(
      portal_type='HTTP Exchange',
      validation_state='confirmed',
    ):
  if exchange.getValidationState() == 'confirmed':
    exchange.activate(activity='SQLDict', tag=tag).HTTPExchange_setFollowUpAndInquiry()
    exchange.acknowledge()
