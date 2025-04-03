for brain in context.getPortalObject().system_event_module.searchFolder(
      portal_type='HTTP Exchange',
      validation_state='confirmed',
    ):
  exchange = brain.getObject()
  if exchange.getValidationState() == 'confirmed':
    exchange.activate(tag=tag).HTTPExchange_setFollowUpAndInquiry()
    exchange.acknowledge()
