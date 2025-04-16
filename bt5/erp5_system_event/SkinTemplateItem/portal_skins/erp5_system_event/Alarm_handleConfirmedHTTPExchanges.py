activate_kw = {'tag': tag}
for exchange in context.getPortalObject().system_event_module.searchFolder(
  portal_type='HTTP Exchange',
  validation_state='confirmed',
):
  if exchange.getValidationState() == 'confirmed':
    # node='' to parallelize the execution on all activity nodes
    exchange.activate(failure_state='non_blocking', node='', **activate_kw).HTTPExchange_setFollowUpAndInquiry()
    exchange.acknowledge()
    exchange.reindexObject(activate_kw=activate_kw)

context.activate(after_tag=tag).getId()
